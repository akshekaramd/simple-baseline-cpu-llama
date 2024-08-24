import subprocess
import re
import csv
import time

def run_program_and_collect_times(program_command, csv_filename, run_count):
    all_times = {
        "AK - Token Generation time": [],
        "load time": [],
        "sample time": [],
        "prompt eval time": [],
        "eval time": [],
        "total time": []
    }

    # Regular expressions to capture the times
    token_gen_regex = re.compile(r"AK - main\.cpp - Token Generation time:\s*(\d+)\s*milliseconds")
    llama_time_regex = re.compile(r"llama_print_timings:\s+(\S+ time)\s*=\s*([\d.]+)\s*ms")
    prompt_eval_regex = re.compile(r"llama_print_timings:\s+prompt eval time\s*=\s*([\d.]+)\s*ms\s*/\s*([\d.]+)\s*tokens.*")

    for i in range(run_count):
        # Run the program and capture stdout and stderr
        result = subprocess.run(program_command, shell=True, capture_output=True, text=True)

        # Search both stdout and stderr for the times
        stdout_matches = token_gen_regex.findall(result.stdout) + llama_time_regex.findall(result.stdout)
        stderr_matches = token_gen_regex.findall(result.stderr) + llama_time_regex.findall(result.stderr)

        # Special handling for prompt eval time
        stdout_prompt_eval = prompt_eval_regex.findall(result.stdout)
        stderr_prompt_eval = prompt_eval_regex.findall(result.stderr)

        # Combine matches
        matches = stdout_matches + stderr_matches
        prompt_eval_matches = stdout_prompt_eval + stderr_prompt_eval

        # Collect all found times
        for match in matches:
            if isinstance(match, tuple):
                time_type, time_value = match
                time_type = time_type.strip()
                all_times[time_type].append(float(time_value))
            else:
                all_times["AK - Token Generation time"].append(float(match))
        
        # Handle prompt eval time separately
        for match in prompt_eval_matches:
            time_value = match[0]  # Extract the prompt eval time in milliseconds
            all_times["prompt eval time"].append(float(time_value))

        print(f"Run {i + 1}: Collected times.")

        # Delay before the next run
        if i < run_count - 1:
            print("Waiting for 5 seconds before the next run...")
            time.sleep(5)

    # Write results to CSV
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        headers = ["Time Type"] + [f"Run {i+1} (ms)" for i in range(run_count)] + ["Average (ms)"]
        writer.writerow(headers)

        for time_type, times in all_times.items():
            # Ensure all runs have a value (fill missing with None)
            while len(times) < run_count:
                times.append(None)
            # Calculate the average manually
            total_sum = sum([t for t in times if t is not None])
            count = len([t for t in times if t is not None])
            average_time = total_sum / count if count > 0 else None
            writer.writerow([time_type] + times + [average_time])

        print(f"All times and averages written to {csv_filename}.")

if __name__ == "__main__":
    program_command = input("Enter the program command to run: ")
    csv_filename = input("Enter the CSV filename to save the results: ")
    run_count = int(input("Enter the number of times to run the program: "))

    run_program_and_collect_times(program_command, csv_filename, run_count)

