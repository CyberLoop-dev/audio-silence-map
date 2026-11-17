import argparse,csv,json,sys
from pathlib import Path
from silence_map import analyze_wav

def main():
    parser=argparse.ArgumentParser(description="Find quiet intervals in a PCM WAV file.")
    parser.add_argument("wav",type=Path)
    parser.add_argument("--threshold",type=float,default=-42.0,help="Silence threshold in dBFS")
    parser.add_argument("--window-ms",type=int,default=100)
    parser.add_argument("--min-duration",type=float,default=0.4)
    parser.add_argument("--format",choices=("text","json","csv"),default="text")
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    try: intervals=analyze_wav(args.wav,args.threshold,args.window_ms,args.min_duration)
    except (OSError,ValueError) as exc:
        print(f"error: {exc}",file=sys.stderr);return 2
    if args.format=="json": result=json.dumps(intervals,indent=2)
    elif args.format=="csv":
        import io
        buffer=io.StringIO(newline="");writer=csv.DictWriter(buffer,fieldnames=["start","end","duration"]);writer.writeheader();writer.writerows(intervals);result=buffer.getvalue().rstrip()
    else:
        result="Found "+str(len(intervals))+" quiet interval(s)\n"+"\n".join(f"{x['start']:.2f}s – {x['end']:.2f}s ({x['duration']:.2f}s)" for x in intervals)
    if args.output: args.output.write_text(result+"\n",encoding="utf-8")
    else: print(result)
    return 0

if __name__=="__main__": raise SystemExit(main())
