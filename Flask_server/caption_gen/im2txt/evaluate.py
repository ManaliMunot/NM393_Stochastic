from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import math
import os.path
import time


import numpy as np
import tensorflow as tf

from im2txt import configuration
from im2txt import show_and_tell_model

FLAGS = tf.flags.FLAGS

tf.flags.DEFINE_string("input_file_pattern", "",
                       "File pattern of sharded TFRecord input files.")
tf.flags.DEFINE_string("checkpoint_dir", "",
                       "Directory containing model checkpoints.")
tf.flags.DEFINE_string("eval_dir", "", "Directory to write event logs.")

tf.flags.DEFINE_integer("eval_interval_secs", 600,
                        "Interval between evaluation runs.")
tf.flags.DEFINE_integer("num_eval_examples", 10132,
                        "Number of examples for evaluation.")

tf.flags.DEFINE_integer("min_global_step", 5000,
                        "Minimum global step to run evaluation.")

tf.logging.set_verbosity(tf.logging.INFO)


def evaluate_model(sess, model, global_step, summary_writer, summary_op):
  """Computes perplexity-per-word over the evaluation dataset.

  Summaries and perplexity-per-word are written out to the eval directory.

  Args:
    sess: Session object.
    model: Instance of ShowAndTellModel; the model to evaluate.
    global_step: Integer; global step of the model checkpoint.
    summary_writer: Instance of FileWriter.
    summary_op: Op for generating model summaries.
  """
  # Log model summaries on a single batch.
  summary_str = sess.run(summary_op)
  summary_writer.add_summary(summary_str, global_step)

  # Compute perplexity over the entire dataset.
  num_eval_batches = int(
      math.ceil(FLAGS.num_eval_examples / model.config.batch_size))

  start_time = time.time()
  sum_losses = 0.
  sum_weights = 0.
  for i in range(num_eval_batches):
    cross_entropy_losses, weights = sess.run([
        model.target_cross_entropy_losses,
        model.target_cross_entropy_loss_weights
    ])
    sum_losses += np.sum(cross_entropy_losses * weights)
    sum_weights += np.sum(weights)
    if not i % 100:
      tf.logging.info("Computed losses for %d of %d batches.", i + 1,
                      num_eval_batches)
  eval_time = time.time() - start_time

  perplexity = math.exp(sum_losses / sum_weights)
  tf.logging.info("Perplexity = %f (%.2g sec)", perplexity, eval_time)
