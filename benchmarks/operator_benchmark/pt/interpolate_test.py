import operator_benchmark as op_bench
import torch

"""Microbenchmarks for interpolate operator."""


class InterpolateBenchmark(op_bench.TorchBenchmarkBase):
    def init(self, input_size, output_size, channels_last=False, interp_mode='linear'):

        input_image = torch.randint(0, 256, size=input_size, dtype=torch.float, device='cpu',
                                    requires_grad=self.auto_set())
        if channels_last:
            if input_image.ndim == 4:
                input_image = input_image.contiguous(memory_format=torch.channels_last)
            elif input_image.ndim == 5:
                input_image = input_image.contiguous(memory_format=torch.channels_last_3d)
            else:
                raise ValueError(
                    f"Can not set channels_last to the input of {input_image.ndim} dims"
                )

        ndim_to_mode = {
            3: 'linear',
            4: 'bilinear',
            5: 'trilinear',
        }

        mode = interp_mode
        align_corners = False

        if "nearest" == mode:
            align_corners = None
        if "linear" == mode:
            mode = ndim_to_mode[input_image.ndim]

        self.inputs = {
            "input_image": input_image,
            "output_size": output_size,
            "mode": mode,
            "align_corners": align_corners,
        }

        self.set_module_name("interpolate")

    def forward(self, input_image, output_size, mode, align_corners):
        return torch.nn.functional.interpolate(input_image, size=output_size, mode=mode,
                                               align_corners=align_corners)


config_short = op_bench.config_list(
    attr_names=["input_size", "output_size"],
    attrs=[
        [(1, 3, 60, 40), (24, 24)],
        [(1, 3, 600, 400), (240, 240)],
        [(1, 3, 320, 320), (256, 256)],
    ],
    cross_product_configs={
        'channels_last': [True, False],
        'interp_mode': ["nearest", "linear", "bicubic"],
    },
    tags=["short"],
)


config_long = op_bench.config_list(
    attr_names=["input_size", "output_size"],
    attrs=[
        [(1, 3, 320, 320), (512, 512)],
        [(1, 3, 500, 500), (256, 256)],
        [(1, 3, 500, 500), (800, 800)],

        [(2, 128, 64, 46), (128, 128)],
        [(2, 128, 64, 46), (32, 24)],
    ],
    cross_product_configs={
        'channels_last': [True, False],
        'interp_mode': ["nearest", "linear", "bicubic"],
    },
    tags=["long"],
)


config_3d = op_bench.config_list(
    # no channels_last for 3D tensors
    attr_names=["input_size", "output_size"],
    attrs=[
        [(4, 512, 320), (256,)],
        [(4, 512, 320), (512,)],
    ],
    cross_product_configs={
        'interp_mode': ["nearest", "linear"],
    },
    tags=["long"],
)


config_5d = op_bench.config_list(    
    attr_names=["input_size", "output_size"],
    attrs=[
        [(1, 3, 16, 320, 320), (8, 256, 256)],
        [(1, 3, 16, 320, 320), (32, 512, 512)],
    ],
    cross_product_configs={
        'channels_last': [True, False],
        'interp_mode': ["nearest", "linear"],
    },
    tags=["long"],
)


for config in (config_short, config_long, config_3d, config_5d):
    op_bench.generate_pt_test(config, InterpolateBenchmark)


if __name__ == "__main__":
    op_bench.benchmark_runner.main()
