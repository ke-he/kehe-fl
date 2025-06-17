import time

import numpy as np

from kehe_fl_s2.utils.common.project_constants import ProjectConstants


class ModelService:
    def __init__(self, agg = False):
        self.__isTraining = False
        self.__weights = None
        self.__x = None
        self.__y = None
        self.__iterationCount = 0

    def __sgd(self, theta):
        x = self.__x
        y = self.__y
        n = len(x)
        alpha = ProjectConstants.FL_ALPHA
        epochs = ProjectConstants.FL_EPOCHS

        for _ in range(epochs):
            indices = np.arange(n)
            np.random.shuffle(indices)
            for i in indices:
                xi = x[i]
                yi = y[i]
                pred = theta[0] + theta[1] * xi
                error = pred - yi
                grad = np.array([error, error * xi])
                theta -= alpha * grad
                self.__iterationCount += 1
        return theta

    def predict(self, x):
        if self.__weights is None:
            print("[MQTTAggServer] No weights")
            return None
        return self.__weights[0] + self.__weights[1] * x

    def start_training(self, data):
        if not self.__isTraining:
            print("[ModelService] Starting training...")
            self.__isTraining = True

            co2_values = []
            temperature_values = []
            for client_data in data:
                for entry in client_data:
                    co2_values.append(float(entry["co2"]))
                    temperature_values.append(float(entry["temperature"]))

            self.__x = np.array(co2_values)
            self.__y = np.array(temperature_values)

            if self.__weights is None or np.any(np.isnan(self.__weights)):
                self.__weights = np.zeros(2)

            start_time = time.time()
            self.__weights = self.__sgd(self.__weights)
            end_time = time.time()

            print(f"[ModelService] Training completed in {end_time - start_time:.2f} seconds.")
            print(f"[ModelService] Final weights: {self.__weights}")

            self.__isTraining = False
        else:
            print("[ModelService] Training already in progress.")

    def check_training_status(self):
        if self.__isTraining:
            return self.__iterationCount, self.__weights
        else:
            print("[ModelService] No training in progress.")
            return None

    def get_weights(self):
        return self.__weights

    def set_weights(self, weights):
        self.__weights = weights
        return

    #FedAvg
    @staticmethod
    def aggregate_weights(weights):
        return np.mean(weights, axis=0)

    @staticmethod
    def unpack_training_status(data):
        test = data.split(",")
        if len(test) == 2:
            try:
                iterationCount = int(test[0])
                weights = np.array([float(i) for i in test[1].split()])
                return iterationCount, weights
            except ValueError:
                print("[ModelService] Error unpacking training status data")
        else:
            print("[ModelService] Invalid training status data format")