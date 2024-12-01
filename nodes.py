import os

import numpy as np

import folder_paths

from moviepy import ImageClip, AudioClip 
from server import PromptServer
from aiohttp import web


class ImageClipNode:
    """
    ComfyUI Node for creating and handling ImageClip objects.

    This node processes an input image and returns an ImageClip representation of it.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """
        Defines the input types for the node.
        """
        return {
            "required": {
                "image": ("IMAGE",),
                "is_mask": ("BOOLEAN", {
                    "default": False,
                }),
                "transparent": ("BOOLEAN", {
                    "default": True,
                }),
                "fromalpha": ("BOOLEAN", {
                    "default": False,
                }),
                "duration": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 10.0,
                    "step": 0.1,
                }),
            }
        }

    RETURN_TYPES = ("VideoCLIP",)
    FUNCTION = "create_clip"
    CATEGORY = "Media Processing"

    def create_clip(self, image, is_mask, transparent, fromalpha, duration):
        """
        Converts the input image into an ImageClip.
        """
        # Convert image to numpy array
        img = np.array(image)

        # Create an ImageClip
        clip = ImageClip(
            img, 
            is_mask=is_mask, 
            transparent=transparent, 
            fromalpha=fromalpha, 
            duration=duration
        )

        # Process output, e.g., resizing or storing metadata if needed
        return (clip,)


class AudioDurationNode:
    """
    A node to calculate the duration of an audio file loaded in ComfyUI.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        """
        Defines the inputs for the node.
        """
        return {
            "required": {
                "audio": ("AUDIO",),
            }
        }

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "calculate_duration"
    CATEGORY = "audio"

    def calculate_duration(self, audio):
        """
        Calculates the duration of the input audio in seconds.
        """
        # Extract waveform and sample rate
        waveform = audio["waveform"]
        sample_rate = audio["sample_rate"]

        # Calculate duration
        duration = waveform.shape[-1] / sample_rate  # Total samples divided by sample rate

        return (duration,)



class SaveVideo:
    """
    ComfyUI Node for saving VideoCLIP objects to a video file.
    """
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""

    @classmethod
    def INPUT_TYPES(cls):
        """
        Defines the input types for the node.
        """
        return {
            "required": {
                "video_clip": ("VideoCLIP",),
                "audio": ("AUDIO",),
                "filename_prefix": ("STRING", {"default": "video/ComfyUI"}),
                "fps": ("INT", {"default": 24, "min": 1, "max": 60}),
                "codec": ("STRING", {"default": "libx264"}),
                "audio_codec": ("STRING", {"default": "aac"}),
                "audio_bitrate": ("STRING", {"default": "128k"}),
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "save_video"

    OUTPUT_NODE = True

    CATEGORY = "video"

    def save_video(
        self,
        video_clip,
        audio,
        filename_prefix="ComfyUI",
        fps=24,
        codec="libx264",
        audio_codec="aac",
        audio_bitrate="128k",
    ):
        """
        Saves a VideoCLIP object to a video file, optionally including audio.
        """
        filename_prefix += self.prefix_append
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(
            filename_prefix, self.output_dir
        )

        # Ensure output folder exists
        os.makedirs(full_output_folder, exist_ok=True)

        # Generate unique file name
        file = f"{filename}_{counter:05}_.mp4"
        output_path = os.path.join(full_output_folder, file)

        # Save the video clip
        video_clip.write_videofile(
            output_path,
            fps=fps,
            audio=audio,
        )

        # Metadata or additional operations if required
        results = {
            "filename": file,
            "subfolder": subfolder,
            "type": self.type,
        }
        return {"ui": {"video": [results]}}


# Map the node for UI integration
NODE_CLASS_MAPPINGS = {
    "ImageClipNode": ImageClipNode,
    "AudioDurationNode": AudioDurationNode,
    "SaveVideo": SaveVideo,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageClipNode": "Image Clip Node",
    "AudioDurationNode": "Audio Duration Node",
    "SaveVideo": "Save Video Node",
}
