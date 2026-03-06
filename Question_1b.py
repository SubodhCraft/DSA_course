def keyword_segmentation(user_query, marketing_keywords_dictionary):

    keyword_set = set(marketing_keywords_dictionary)
    memo = {}

    def backtrack(substring):

        if substring in memo:
            return memo[substring]

        if substring == "":
            return [""]

        results = []

        for i in range(1, len(substring) + 1):
            prefix = substring[:i]

            if prefix in keyword_set:
                remaining = substring[i:]
                suffix_sentences = backtrack(remaining)

                for sentence in suffix_sentences:
                    if sentence == "":
                        results.append(prefix)
                    else:
                        results.append(prefix + " " + sentence)

        memo[substring] = results
        return results

    return backtrack(user_query)


# -------- Example Use Case --------

user_query = "nepaltrekkingguide"
marketing_keywords_dictionary = ["nepal", "trekking", "guide", "nepaltrekking"]

result = keyword_segmentation(user_query, marketing_keywords_dictionary)

print("User Search Query:", user_query)
print("Marketing Keywords Dictionary:", marketing_keywords_dictionary)
print("-----")

if result:
    print("Possible Keyword Sentences:")
    for sentence in result:
        print("-", sentence)

    print("Explanation:")
    print("The search query can be segmented using valid keywords from the dictionary.")
else:
    print("No valid keyword segmentation found.")