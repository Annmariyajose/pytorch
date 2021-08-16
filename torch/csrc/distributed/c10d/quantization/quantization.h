// (c) Facebook, Inc. and its affiliates. Confidential and proprietary.

#pragma once


#include <ATen/ATen.h>
#include <vector>

namespace torch {
namespace distributed {
namespace c10d {
namespace quantization {

at::Tensor _float_to_bfloat16_cpu(const at::Tensor& input);
at::Tensor _bfloat16_to_float_cpu(const at::Tensor& input);

#ifdef USE_C10D_NCCL
at::Tensor _float_to_bfloat16_gpu(const at::Tensor& input);
at::Tensor _bfloat16_to_float_gpu(const at::Tensor& input);
#endif

} // namespace quantization
} // namespace c10d
} // namespace distributed
} // namespace torch
