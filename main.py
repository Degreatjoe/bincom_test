'''
Docstring for main

this is the main file for the assignment,
it runs all the functins and features 
of the test questions
'''

from lib import (
    COLOUR_DATA,
    calculate_mean,
    calculate_variance,
    calculate_median,
    calculate_mode,
    calculate_probability,
    recursive_search,
    random_binary_to_decimal,
    sum_first_n_fibonacci
)

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
 
    # 6. Uncomment to actually write to your own PostgreSQL instance:
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