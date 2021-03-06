# Lint as: python3
# Copyright 2019 DeepMind Technologies Limited. All Rights Reserved.
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
"""Padding module for Haiku."""

from typing import Sequence, Union, Tuple

from haiku._src import utils
from haiku._src.typing import PadFnOrFns


def valid(effective_kernel_size: int) -> Tuple[int, int]:
  """No padding."""
  del effective_kernel_size
  return (0, 0)


def same(effective_kernel_size: int) -> Tuple[int, int]:
  """Pads such that the output size matches input size for stride=1."""
  return ((effective_kernel_size - 1) // 2, effective_kernel_size // 2)


def full(effective_kernel_size: int) -> Tuple[int, int]:
  """Maximal padding whilst not convolving over just padded elements."""
  return (effective_kernel_size - 1, effective_kernel_size - 1)


def causal(effective_kernel_size: int) -> Tuple[int, int]:
  """Pre-padding such that output has no dependence on the future."""
  return (effective_kernel_size - 1, 0)


def reverse_causal(effective_kernel_size: int) -> Tuple[int, int]:
  """Post-padding such that output has no dependence on the past."""
  return (0, effective_kernel_size - 1)


def create(
    padding: PadFnOrFns,
    kernel: Union[int, Sequence[int]],
    rate: Union[int, Sequence[int]],
    n: int,
) -> Sequence[Tuple[int, int]]:
  """Generates the padding required for a given padding algorithm.

  Args:
    padding: callable or list of callables of length n. The callables take an
      integer representing the effective kernel size (kernel size when the rate
      is 1) and return a list of two integers representing the padding before
      and padding after for that dimension.
    kernel: int or list of ints of length n. The size of the kernel for each
      dimension. If it is an int it will be replicated for the non channel and
      batch dimensions.
    rate: int or list of ints of length n. The dilation rate for each dimension.
      If it is an int it will be replicated for the non channel and batch
      dimensions.
    n: the number of spatial dimensions.

  Returns:
    A sequence of length n containing the padding for each element. These are of
    the form ``[pad_before, pad_after]``.
  """
  # The effective kernel size includes any holes/gaps introduced by the
  # dilation rate. It's equal to kernel_size when rate == 1.
  effective_kernel_size = map(  # pylint: disable=deprecated-lambda
      lambda kernel, rate: (kernel - 1) * rate + 1,
      utils.replicate(kernel, n, "kernel"), utils.replicate(rate, n, "rate"))
  paddings = map(  # pylint: disable=deprecated-lambda
      lambda x, y: x(y), utils.replicate(padding, n, "padding"),
      effective_kernel_size)

  return tuple(paddings)
