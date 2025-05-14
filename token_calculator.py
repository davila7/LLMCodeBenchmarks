# Define the parameters
num_calls = 100
words_per_call = 100

# Tokenization assumption: 1 word ≈ 1.33 tokens
tokens_per_word = 1.33

total_words = num_calls * words_per_call
total_tokens = total_words * tokens_per_word

# Prices
input_token_price_per_million = 0.59
output_token_price_per_million = 0.79

# Calculate the total cost
input_cost = (total_tokens / 1_000_000) * input_token_price_per_million
output_cost = (total_tokens / 1_000_000) * output_token_price_per_million
total_cost = input_cost + output_cost

print(total_cost)