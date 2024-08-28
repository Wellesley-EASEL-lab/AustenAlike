from openai import OpenAI
import re
import sys

key = "INSERT API KEY"
client = OpenAI(api_key=key)
from collections import Counter

def query(c,characters,mode="plain"):
  if mode == "plain":
    q = f"Which character is {c} most similar to (other than {c})? Respond with only a number. Do not choose {characters.index(c)+1}."
  if mode == "reasoning":
    q = f"Which character is {c} most similar to (other than {c})? Describe your reasoning and then reply with the number of the character. Do not choose {characters.index(c)+1}."
  if mode == "top10":
    q = f"List the 10 characters that are most similar to {c} (other than {c}). Consider characters from all Austen novels. Reply with just their numbers. Do not choose {characters.index(c)+1}."
  response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
    {
    "role": "system",
    "content": [
    {
    "type": "text",
    "text": "Consider the following list of Jane Austen characters:\n\n1. Anna Weston\n2. Augusta Elton\n3. Emma Woodhouse\n4. Frank Churchill\n5. George Knightley\n6. Harriet Smith\n7. Isabella Knightley\n8. Jane Fairfax\n9. John Knightley\n10. Miss Bates\n11. Mr. Weston\n12. Mr. Woodhouse\n13. Mr. Perry\n14. Mrs. Cole\n15. Philip Elton\n16. Robert Martin\n17. Dr. Grant\n18. Edmund Bertram\n19. Fanny Price\n20. Henry Crawford\n21. Julia Bertram\n22. Lady Bertram\n23. Maria Bertram\n24. Mary Crawford\n25. Mr. Price\n26. Mr. Rushworth\n27. Mr. Yates\n28. Mrs. Grant\n29. Mrs. Norris\n30. Mrs. Price\n31. Mrs. Rushworth\n32. Sir Thomas Bertram\n33. Susan Price\n34. Tom Bertram\n35. William Price\n36. Catherine Morland\n37. Eleanor Tilney\n38. Frederick Tilney\n39. General Tilney\n40. Henry Tilney\n41. Isabella Thorpe\n42. James Morland\n43. John Thorpe\n44. Mr. Allen\n45. Mrs. Allen\n46. Mrs. Morland\n47. Mrs. Thorpe\n48. Admiral Croft\n49. Anne Elliot\n50. Captain Benwick\n51. Captain Harville\n52. Charles Hayter\n53. Charles Musgrove\n54. Elizabeth Elliot\n55. Henrietta Musgrove\n56. Lady Russell\n57. Louisa Musgrove\n58. Mary Musgrove\n59. Mr. Shepherd\n60. Mrs. Clay\n61. Mrs. Croft\n62. Mrs. Harville\n63. Mrs. Musgrove\n64. Mr. Musgrove\n65. Mrs. Smith\n66. Sir Walter Elliot\n67. William Elliot\n68. Captain Wentworth\n69. Caroline Bingley\n70. Charles Bingley\n71. Charlotte Lucas\n72. Colonel Fitzwilliam\n73. Mr. Gardiner\n74. Elizabeth Bennet\n75. Fitzwilliam Darcy\n76. George Wickham\n77. Georgiana Darcy\n78. Jane Bennet\n79. Kitty Bennet\n80. Lady Catherine de Bourgh\n81. Lady Lucas\n82. Lydia Bennet\n83. Mary Bennet\n84. Mr. Bennet\n85. Mrs. Bennet\n86. Mr. Phillips\n87. Mrs. Gardiner\n88. Mrs. Hurst\n89. Mr. Hurst\n90. Mrs. Phillips\n91. Sir William Lucas\n92. William Collins\n93. Anne Steele\n94. Charlotte Palmer\n95. Colonel Brandon\n96. Edward Ferrars\n97. Elinor Dashwood\n98. Fanny Dashwood\n99. John Dashwood\n100. John Willoughby\n101. Lady Middleton\n102. Lucy Steele\n103. Margaret Dashwood\n104. Marianne Dashwood\n105. Mrs. Dashwood\n106. Mrs. Jennings\n107. Robert Ferrars\n108. Sir John Middleton\n109. Thomas Palmer"
    }
    ]
    },
    {
    "role": "user",
    "content": [
    {
      "type": "text",
      "text": q
    }
    ]
    },
    {
    "role": "assistant",
    "content": [
    {
    "type": "text",
    "text": "Emma Woodhouse"
    }
    ]
    }
    ],
    temperature=0.2,
    max_tokens=256,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    response_format={
    "type": "text"
    }
    )
  answer = response.choices[0].message.content
  return answer

def most_common(data,c):
  answers = data[c]
  counts = Counter(answers)
  return counts.most_common(1)[0][0]

def export(data,mode):
  with open(f"{mode}_results_t02.tsv",'w') as of:
    header = "Character\tMostCommon\t" + '\t'.join([f"C{i+1}" for i in range(len(data[list(data.keys())[0]]))]) + "\n"
    of.write(header)
    for c in data:
      most = most_common(data,c)
      line = f"{c}\t{most}\t"+"\t".join(data[c])+"\n"
      of.write(line)

def main():
  mode = sys.argv[1]
  with open("../characters.tsv",'r') as of:
    characters = [c.strip() for c in of.readlines()]
  answers = {}
  for c in characters:
    for i in range(5):
      answer = query(c,characters,mode)
      if mode == "top10":
        if ',' in answer:
          l = answer.split(',')
        else:
          l = answer.split('\n')
        print(l)
        numbers = []
        for a in l:
          numbers += [int(i) for i in re.findall(r'\d+', a)]
      else:
        answer = answer.split('\n')[-1]
        numbers = [int(i) for i in re.findall(r'\d+', answer)]
      for n in numbers:
        assert n in list(range(1,110))
        chosen = characters[n-1]
        print(c,chosen)
        if c in answers:
          answers[c].append(chosen)
        else:
          answers[c] = [chosen]
  print(answers)
  export(answers,mode)

main()