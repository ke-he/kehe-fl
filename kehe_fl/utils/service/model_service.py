import time
from glob import glob

import numpy as np
import pandas as pd

from kehe_fl.utils.common.project_constants import ProjectConstants


class ModelService:
    def __init__(self, main = False):
        self.__isTraining = False
        self.__weights = None
        self.__x = None
        self.__y = None
        self.__iterationCount = 0

    def __loss(self, theta):
        predictions = theta[0] + theta[1] * self.__x
        return np.mean((predictions - self.__y) ** 2) / 2

    def __gradient(self, theta):
        epsilon = 1e-4
        epsilon_0 = np.array([epsilon, 0])
        epsilon_1 = np.array([0, epsilon])
        d_theta_0 = (self.__loss(theta + epsilon_0) - self.__loss(theta - epsilon_0)) / (2 * epsilon)
        d_theta_1 = (self.__loss(theta + epsilon_1) - self.__loss(theta - epsilon_1)) / (2 * epsilon)
        return np.array([d_theta_0, d_theta_1])

    def __gradient_descent(self, theta):
        for _ in range(ProjectConstants.FL_ITERATIONS):
            theta -= ProjectConstants.FL_ALPHA * self.__gradient(theta)
            self.__iterationCount += 1
        return theta

    def predict(self, x):
        if self.__weights is None:
            print("[MQTTAggServer] No weights")
            return None
        return self.__weights[0] + self.__weights[1] * x

    def start_training(self, data_path: str):
        if not self.__isTraining:
            print("[FederatedLearningService] Starting training...")
            self.__isTraining = True

            data_files = glob(f"{data_path}/*.csv")
            data = pd.concat([pd.read_csv(file) for file in data_files], ignore_index=True)
            self.__x = data["co2"].values
            self.__y = data["temperature"].values

            self.__weights = np.zeros(2)

            start_time = time.time()
            self.__weights = self.__gradient_descent(self.__weights)
            end_time = time.time()

            print(f"[FederatedLearningService] Training completed in {end_time - start_time:.2f} seconds.")
            print(f"[FederatedLearningService] Final weights: {self.__weights}")

            self.__isTraining = False
        else:
            print("[FederatedLearningService] Training already in progress.")

    def check_training_status(self):
        if self.__isTraining:
            return self.__iterationCount, self.__weights
        else:
            print("[FederatedLearningService] No training in progress.")
            return None

    def get_weights(self):
        return self.__weights