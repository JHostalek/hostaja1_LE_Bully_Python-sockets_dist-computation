if __name__ == '__main__':
    from pydub import AudioSegment

    # Load the audio file
    audio = AudioSegment.from_mp3("original.mp3")

    # Calculate the step size (in milliseconds)
    step_size = int(audio.duration_seconds * 1000 // 20)

    # Split the audio file into 20 parts
    parts = [audio[i:i + step_size] for i in range(0, len(audio), step_size)]

    # Save each part to a separate file
    for i, part in enumerate(parts):
        part.export("task{}.mp3".format(i), format="mp3")
