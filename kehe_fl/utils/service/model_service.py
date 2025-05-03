import time
from glob import glob

import numpy as np
import pandas as pd

from kehe_fl.utils.common.project_constants import ProjectConstants


class ModelService:
    def __init__(self, main = False):
        self._isTraining = False
        self.weights = None
        self.x = None
        self.y = None
        self._iterationCount = 0

    def loss(self, theta):
        predictions = theta[0] + theta[1] * self.x
        return np.mean((predictions - self.y) ** 2) / 2

    def gradient(self, theta):
        epsilon = 1e-4
        epsilon_0 = np.array([epsilon, 0])
        epsilon_1 = np.array([0, epsilon])
        d_theta_0 = (self.loss(theta + epsilon_0) - self.loss(theta - epsilon_0)) / (2 * epsilon)
        d_theta_1 = (self.loss(theta + epsilon_1) - self.loss(theta - epsilon_1)) / (2 * epsilon)
        return np.array([d_theta_0, d_theta_1])

    def gradient_descent(self, theta):
        for _ in range(ProjectConstants.FL_ITERATIONS):
            theta -= ProjectConstants.FL_ALPHA * self.gradient(theta)
            self._iterationCount += 1
        return theta

    def predict(self, x):
        if self.weights is None:
            raise ValueError("Model is not trained yet.")
        return self.weights[0] + self.weights[1] * x

    def start_training(self, data_path: str):
        if not self._isTraining:
            print("[FederatedLearningService] Starting training...")
            self._isTraining = True

            data_files = glob(f"{data_path}/*.csv")
            data = pd.concat([pd.read_csv(file) for file in data_files], ignore_index=True)
            self.x = data["co2"].values
            self.y = data["temperature"].values

            self.weights = np.zeros(2)

            start_time = time.time()
            self.weights = self.gradient_descent(self.weights)
            end_time = time.time()

            print(f"[FederatedLearningService] Training completed in {end_time - start_time:.2f} seconds.")
            print(f"[FederatedLearningService] Final weights: {self.weights}")

            self._isTraining = False
        else:
            print("[FederatedLearningService] Training already in progress.")

    def check_training_status(self):
        if self._isTraining:
            return self._iterationCount, self.weights
        else:
            print("[FederatedLearningService] No training in progress.")
            return None