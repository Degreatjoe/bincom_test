'''Bincom basic dev test
An analysis of staff dress colors for the week 
based on the data provided.

Author: Great Joseph
python 3x
'''
# first i had place the data in a list,
# then i will use the list to calculate the mean, 
# variance, etc.
import random
from collections import Counter
import statistics


COLOUR_DATA = [
    # Monday
    "GREEN", "YELLOW", "GREEN", "BROWN", "BLUE", "PINK", "BLUE", "YELLOW",
    "ORANGE", "CREAM", "ORANGE", "RED", "WHITE", "BLUE", "WHITE", "BLUE",
    "BLUE", "BLUE", "GREEN",
    # Tuesday  (note: ARSH / BLEW look like data-entry typos in the source)
    "ARSH", "BROWN", "GREEN", "BROWN", "BLUE", "BLUE", "BLEW", "PINK",
    "PINK", "ORANGE", "ORANGE", "RED", "WHITE", "BLUE", "WHITE", "WHITE",
    "BLUE", "BLUE", "BLUE",
    # Wednesday
    "GREEN", "YELLOW", "GREEN", "BROWN", "BLUE", "PINK", "RED", "YELLOW",
    "ORANGE", "RED", "ORANGE", "RED", "BLUE", "BLUE", "WHITE", "BLUE",
    "BLUE", "WHITE", "WHITE",
    # Thursday
    "BLUE", "BLUE", "GREEN", "WHITE", "BLUE", "BROWN", "PINK", "YELLOW",
    "ORANGE", "CREAM", "ORANGE", "RED", "WHITE", "BLUE", "WHITE", "BLUE",
    "BLUE", "BLUE", "GREEN",
    # Friday
    "GREEN", "WHITE", "GREEN", "BROWN", "BLUE", "BLUE", "BLACK", "WHITE",
    "ORANGE", "RED", "RED", "RED", "WHITE", "BLUE", "WHITE", "BLUE",
    "BLUE", "BLUE", "WHITE",
]

# ============HELPER FUNCTIONS========================

# to calculate the mean, variance, etc, for colors 
# i first give each color a numerical value, 
# then i will use the values to calculate the mean, 
# variance, etc.

def build_colour_codes(colours):
    unique_sorted = sorted(set(colours))
    code_of = {colour: i for i, colour in enumerate(unique_sorted)}
    colour_of = {i: colour for colour, i in code_of.items()}
    return code_of, colour_of

# since this is not a number, finding mean and variance of colors may
# end up giving a decimal value which does not fall under any color,
# so i would establish a function to fined the closest color to the mean and variance values
# def closest_colour(value, colour_of):
#     closest_value = min(colour_of.keys(), key=lambda x: abs(x - value))
#     return colour_of[closest_value]

# or lets try rounding up the value to the nearest whole number and mapping it back to the color
def nearest_colour(value, colour_of):
    """Round a numeric code to the nearest whole number and map back."""
    idx = round(value)
    idx = max(0, min(idx, len(colour_of) - 1))
    return colour_of[idx]

# =================================================================================



def calculate_mean(colors):
    code_of, colour_of = build_colour_codes(colors)
    numeric_values = [code_of[color] for color in colors]
    mean_value = sum(numeric_values) / len(numeric_values)
    return nearest_colour(mean_value, colour_of), mean_value

def calculate_median(colours):
    code_of, colour_of = build_colour_codes(colours)
    codes = [code_of[c] for c in colours]
    med = statistics.median(codes)
    return nearest_colour(med, colour_of), med


def calculate_mode(colours):
    counts = Counter(colours)
    colour, freq = counts.most_common(1)[0]
    return colour, freq, counts

def calculate_variance(colours):
    code_of, _ = build_colour_codes(colours)
    codes = [code_of[c] for c in colours]
    return statistics.pvariance(codes)

def calculate_probability(colours, target_colour="RED"):
    counts = Counter(colours)
    return counts[target_colour] / len(colours)

def recursive_search(lst, target, index=0):
    """
    Linear recursive search.
    Returns the index of `target` in `lst`, or -1 if not found.
    """
    if index >= len(lst):
        return -1
    if lst[index] == target:
        return index
    return recursive_search(lst, target, index + 1)
 
 
# --------------------------------------------------------------------------
# 8: Random 4-digit number of 0s and 1s -> base 10
# --------------------------------------------------------------------------
 
def random_binary_to_decimal():
    binary_digits = [str(random.randint(0, 1)) for _ in range(4)]
    binary_str = "".join(binary_digits)
    decimal_value = int(binary_str, 2)
    return binary_str, decimal_value
 
 
# --------------------------------------------------------------------------
# 9: Sum of the first 50 Fibonacci numbers
# --------------------------------------------------------------------------
 
def sum_first_n_fibonacci(n=50):
    a, b = 0, 1
    total = 0
    for _ in range(n):
        total += a
        a, b = b, a + b
    return total


# i really did not understand this instruction,
# because if this is not changed the whole file won't run
def save_frequencies_to_postgres(counts,
                                  dbname="bincom_test",
                                  user="postgres",
                                  password="your_password",
                                  host="localhost",
                                  port="5432"):
    import psycopg2
 
    conn = psycopg2.connect(
        dbname=dbname, user=user, password=password, host=host, port=port
    )
    cur = conn.cursor()
 
    cur.execute("""
        CREATE TABLE IF NOT EXISTS colour_frequency (
            id SERIAL PRIMARY KEY,
            colour VARCHAR(50) UNIQUE NOT NULL,
            frequency INTEGER NOT NULL
        );
    """)
 
    for colour, freq in counts.items():
        cur.execute("""
            INSERT INTO colour_frequency (colour, frequency)
            VALUES (%s, %s)
            ON CONFLICT (colour) DO UPDATE SET frequency = EXCLUDED.frequency;
        """, (colour, freq))
 
    conn.commit()
    cur.close()
    conn.close()
    print("Saved colour frequencies to PostgreSQL.")




if __name__ == "__main__":
    colours = COLOUR_DATA  # swap for extract_colours_from_html(path) if desired
 
    print("=" * 60)
    print("BINCOM STAFF DRESS-COLOUR ANALYSIS")
    print("=" * 60)
 
    mcolour, mvalue = calculate_mean(colours)
    print(f"1. Mean colour:        {mcolour}  (avg code = {mvalue:.2f})")
 
    mode_c, mode_freq, all_counts = calculate_mode(colours)
    print(f"2. Most worn colour:   {mode_c}  ({mode_freq} times)")
 
    medcolour, medvalue = calculate_median(colours)
    print(f"3. Median colour:      {medcolour}  (median code = {medvalue})")
 
    var = calculate_variance(colours)
    print(f"4. Variance:           {var:.2f}")
 
    prob_red = calculate_probability(colours, "RED")
    print(f"5. P(colour == RED):   {prob_red:.4f}  ({prob_red * 100:.1f}%)")
 
    print("\nFull frequency table:")
    for colour, freq in all_counts.most_common():
        print(f"   {colour:<10} {freq}")
 
    # to save the frequencies to a PostgreSQL database,
    # since i do not have a running PostgreSQL instance, i will comment this out.

    # you need to have a running PostgreSQL instance and the psycopg2 library installed.
    # Make sure to replace "your_password" with your actual PostgreSQL password in the `save_frequencies_to_postgres` function.

    # Uncomment to actually write to your own PostgreSQL instance:
    # save_frequencies_to_postgres(all_counts)
 
    print("\n7. Recursive search demo:")
    numbers = [4, 8, 15, 16, 23, 42]
    target = 23
    result = recursive_search(numbers, target)
    print(f"   Searching for {target} in {numbers} -> index {result}")
 
    print("\n8. Random 4-digit binary -> decimal:")
    b, d = random_binary_to_decimal()
    print(f"   Binary: {b}  ->  Decimal: {d}")
 
    print("\n9. Sum of first 50 Fibonacci numbers:")
    print(f"   {sum_first_n_fibonacci(50)}")