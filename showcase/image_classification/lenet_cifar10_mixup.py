# Copyright 2019 The FastEstimator Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import tensorflow as tf

from fastestimator.architecture.lenet import LeNet
from fastestimator.estimator.estimator import Estimator
from fastestimator.estimator.trace import Accuracy, ConfusionMatrix
from fastestimator.network.loss import MixUpLoss
from fastestimator.network.model import ModelOp, build
from fastestimator.network.network import Network
from fastestimator.pipeline.augmentation import MixUpBatch
from fastestimator.pipeline.pipeline import Pipeline
from fastestimator.pipeline.preprocess import Minmax


def get_estimator(epochs=2, batch_size=32, alpha=1.0):
    (x_train, y_train), (x_eval, y_eval) = tf.keras.datasets.cifar10.load_data()
    data = {"train": {"x": x_train, "y": y_train}, "eval": {"x": x_eval, "y": y_eval}}
    num_classes = 10

    pipeline = Pipeline(batch_size=batch_size,
                        data=data,
                        ops=Minmax(inputs="x", outputs="x"))

    model = build(keras_model=LeNet(input_shape=x_train.shape[1:], classes=num_classes),
                  loss=MixUpLoss(tf.losses.SparseCategoricalCrossentropy(), true_key="y", pred_key="y_pred",
                                 lambda_key="lambda"),
                  optimizer="adam")

    network = Network(ops=[
        MixUpBatch(inputs="x", outputs=["x", "lambda"], alpha=alpha, mode="train"),
        ModelOp(inputs="x", model=model, outputs="y_pred")])

    traces = [Accuracy(true_key="y", pred_key="y_pred"),
              ConfusionMatrix(true_key="y", pred_key="y_pred", num_classes=num_classes)]

    estimator = Estimator(network=network, pipeline=pipeline, epochs=epochs, traces=traces)

    return estimator
