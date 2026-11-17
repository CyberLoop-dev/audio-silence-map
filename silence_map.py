import math,struct,wave
from pathlib import Path

def _samples(data,width):
    if width==1: return [(value-128)/128.0 for value in data]
    if width==2: return [value[0]/32768.0 for value in struct.iter_unpack("<h",data)]
    if width==3:
        values=[]
        for i in range(0,len(data)-2,3):
            raw=int.from_bytes(data[i:i+3],"little",signed=True)
            values.append(raw/8388608.0)
        return values
    if width==4: return [value[0]/2147483648.0 for value in struct.iter_unpack("<i",data)]
    raise ValueError("only 8-, 16-, 24-, and 32-bit PCM WAV is supported")

def analyze_wav(path:Path,threshold_dbfs=-42.0,window_ms=100,min_duration=0.4):
    if window_ms<=0 or min_duration<0: raise ValueError("window_ms must be positive and min_duration non-negative")
    threshold=10**(threshold_dbfs/20)
    with wave.open(str(path),"rb") as wav:
        if wav.getcomptype()!="NONE": raise ValueError("compressed WAV is not supported")
        channels,rate,width=wav.getnchannels(),wav.getframerate(),wav.getsampwidth()
        if rate<=0 or channels<=0: raise ValueError("invalid WAV stream")
        frames_per=max(1,round(rate*window_ms/1000))
        frame_bytes=channels*width
        total=wav.getnframes()
        intervals=[];start=None;cursor=0
        while cursor<total:
            count=min(frames_per,total-cursor)
            data=wav.readframes(count)
            samples=_samples(data,width)
            rms=math.sqrt(sum(x*x for x in samples)/len(samples)) if samples else 0
            quiet=rms<=threshold
            left=cursor/rate;right=(cursor+count)/rate
            if quiet and start is None: start=left
            if not quiet and start is not None:
                if left-start>=min_duration: intervals.append({"start":round(start,3),"end":round(left,3),"duration":round(left-start,3)})
                start=None
            cursor+=count
        if start is not None:
            duration=total/rate-start
            if duration>=min_duration: intervals.append({"start":round(start,3),"end":round(total/rate,3),"duration":round(duration,3)})
    return intervals
