Background: The Soundex algorithm is a phonetic algorithm commonly used by libraries and the Census Bureau to represent people’s names as they are pronounced in English. It has the advantage that name variations with minor spelling differences will map to the same representation, as long as they have the same pronunciation in English. Here is how the algorithm works: 
Step 1: Retain the first letter of the name. This may be uppercased or lowercased. 
Step 2: Remove all non-initial occurrences of the following letters: a, e, h, i, o, u, w, y. (To clarify, this step removes all occurrences of the given characters except when they occur in the first position.) 
Step 3: Replace the remaining letters (except the first) with numbers: 5 

• b, f, p, v → 1 • c, g, j, k, q, s, x, z → 2 • d, t → 3 •l→4 • m, n → 5 •r→6 

If two or more letters from the same number group were adjacent in the original name (i.e. before any letter removal is done), then only replace the first of those letters with the corresponding number and ignore the others. 
Step 4: If there are more than 3 digits in the resulting output, then drop the extra ones. 
Step 5: If there are less than 3 digits, then pad at the end with the required number of trailing zeros. 
