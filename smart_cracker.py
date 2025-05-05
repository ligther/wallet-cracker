import os
import subprocess
import random
import hashlib
import multiprocessing
import sys

wallet_file = "wallet.dat"
progress_file = "progress.txt"
found_file = "found_password.txt"

common_words = [
    "jordan", "love", "king", "money", "bitcoin", "admin", "test", "qwerty", "welcome", "summer",
    "password", "freedom", "android", "sunshine", "flower", "moon", "star", "12345", "super"
]

numbers = ["", "123", "1234", "2023", "2024", "321", "111", "007", "999"]
symbols = ["", "!", "@", "#", "$"]

tested_passwords = set()
if os.path.exists(progress_file):
    with open(progress_file, "r") as f:
        tested_passwords = set(line.strip() for line in f if line.strip())

def get_password_hash(password):
    return hashlib.sha1(password.encode()).hexdigest()[:16]

def generate_smart_password():
    word = random.choice(common_words)
    number = random.choice(numbers)
    symbol = random.choice(symbols)
    patterns = [
        word + number,
        number + word,
        word.capitalize() + number,
        word + symbol + number,
        word + number + symbol,
        word*2 + number
    ]
    return random.choice(patterns)

def try_password(password):
    cmd = [
        "python", "pywallet.py",
        "--dumpwallet", f"--wallet={wallet_file}",
        f"--password={password}"
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if "hex privkey" in result.stdout.lower():
        print(f"\n\n=== Password Found! ===\nPassword: {password}\n")
        with open(found_file, "w") as f:
            f.write(password + "\n")
        os._exit(0)

def worker():
    buffer = []
    while True:
        password = generate_smart_password()
        password_hash = get_password_hash(password)
        if password_hash in tested_passwords:
            continue
        print(f"Trying: {password}")
        tested_passwords.add(password_hash)
        buffer.append(password_hash)
        if len(buffer) >= 100:
            with open(progress_file, "a") as f:
                for h in buffer:
                    f.write(h + "\n")
            buffer.clear()
        try_password(password)

if __name__ == "__main__":
    if not os.path.exists(wallet_file):
        print("Wallet file not found!")
        exit(1)
    cpu_count = multiprocessing.cpu_count()
    print(f"Using {cpu_count} CPU cores for brute force...")
    processes = []
    for _ in range(cpu_count):
        p = multiprocessing.Process(target=worker)
        p.start()
        processes.append(p)
    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("Process interrupted by user.")
        sys.exit(1)
