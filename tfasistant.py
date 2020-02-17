from tensorflow import ones_like, equal, log
from keras import backend as K
from tensorflow.python import mul
import tensorflow as tf
from keras import backend as K

def weighted_categorical_crossentropy(weights):
    """
    A weighted version of keras.objectives.categorical_crossentropy
    
    Variables:
        weights: numpy array of shape (C,) where C is the number of classes
    
    Usage:
        weights = np.array([0.5,2,10]) # Class one at 0.5, class 2 twice the normal weights, class 3 10x.
        loss = weighted_categorical_crossentropy(weights)
        model.compile(loss=loss,optimizer='adam')
    """
    
    weights = K.variable(weights)
        
    def loss(y_true, y_pred):
        # scale predictions so that the class probas of each sample sum to 1
        y_pred /= K.sum(y_pred, axis=-1, keepdims=True)
        # clip to prevent NaN's and Inf's
        y_pred = K.clip(y_pred, K.epsilon(), 1 - K.epsilon())
        # calc
        loss = y_true * K.log(y_pred) * weights
        loss = -K.sum(loss, -1)
        return loss
    
    return loss

def weighted_binary_crossentropy(w1, w2):
  '''
  w1 and w2 are the weights for the two classes.
  Computes weighted binary crossentropy
  Use like so:  model.compile(loss=weighted_binary_crossentropy(), optimizer="adam", metrics=["accuracy"])
  '''

    def loss(y_true, y_pred):
        # avoid absolute 0
        y_pred = K.clip(y_pred, K.epsilon(), 1 - K.epsilon())
        ones = ones_like(y_true)
        msk = equal(y_true, ones)
        # tensor of booleans of length == y_true; true means that the true class is 1

        res, _ = tf.map_fn(lambda x: (mul(-log(x[0]), w1) if x[1] is True
                                      else mul(-log(1 - x[0]) w2), x[1]),
                           (y_pred, msk), dtype=(tf.float32, tf.bool))

        return res

    return loss
