import os
import io

import torchaudio
import numpy as np

import folder_paths

from moviepy import ImageClip, AudioClip 
from comfy_extras.nodes_audio import insert_or_replace_vorbis_comment


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

    def create_clip(self, image, duration):
        """
        Converts the input image into an ImageClip.
        """
        # Convert image to numpy array
        img = image.detach().cpu().numpy()[0]
        img = (img * 255).astype(np.uint8)

        # Create an ImageClip
        clip = ImageClip(
            img,
            duration=duration
        )
        clip.show(2)

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



class SaveVideoNode:
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
                "audio": ("AUDIO", ),
                "filename_prefix": ("STRING", {"default": "video/ComfyUI"}),
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
    ):
        """
        Saves a VideoCLIP object to a video file, optionally including audio.
        """

        filename_prefix += self.prefix_append
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(
            filename_prefix, self.output_dir
        )


        audio_file = f"{filename}_{counter:05}_.mp3"
        audio_file_path = os.path.join(full_output_folder, audio_file)
        torchaudio.save(audio_file_path, audio["waveform"][0], audio["sample_rate"])


        # Ensure output folder exists
        os.makedirs(full_output_folder, exist_ok=True)

        # Generate unique file name
        video_file = f"{filename}_{counter:05}_.mp4"
        output_path = os.path.join(full_output_folder, video_file)

        # Save the video clip
        video_clip.write_videofile(
            output_path,
            fps=25,
            audio=audio_file_path,
        )
        video_clip.close()

        os.remove(audio_file_path)

        # Metadata or additional operations if required
        results = {
            "filename": video_file,
            "subfolder": subfolder,
            "type": self.type,
        }
        return {"ui": {"video": [results]}}


# Map the node for UI integration
NODE_CLASS_MAPPINGS = {
    "ImageClipNode": ImageClipNode,
    "AudioDurationNode": AudioDurationNode,
    "SaveVideoNode": SaveVideoNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageClipNode": "Image Clip Node",
    "AudioDurationNode": "Audio Duration Node",
    "SaveVideoNode": "Save Video Node",
}
