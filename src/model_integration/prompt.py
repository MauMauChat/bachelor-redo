#!/usr/bin/env python3

PROMPT_TEMPLATE = """**Prompt:**

**Analyze the following sentences and classify them into one of the given categories.** 
**The Input will be id:sentence** 
**One sentence, one category.**
**Output a well-formed XML snippet that contains a `<result>` tag. Inside `<result>`, for each sentence output exactly the following tags in order:**  
<result>
`<i>...</i>`
`<s>...</s>`
`<c>...</c>`
</result>

**Available categories:**  
- Bezug auf LV
- Nicht verständlich
- Nicht eindeutig zuordenbar
- Negativ
- Positiv
- Neutral, kein Kommentar, äquivalente Symbole, bedeutungslos
- Anregungen, Wünsche

**ALWAYS WRITE IT ONLY LIKE THIS. NOTHING MORE; NOTHING LESS:**
<result>
  <i>1</i>
  <s>Die Vorlesung war sehr spannend und gut strukturiert.</s>
  <c>Positiv</c>
  <i>2</i>
  <s>???</s>
  <c>Nicht verständlich</c>
  <i>3</i>
  <s>Mehr praktische Beispiele wären hilfreich.</s>
  <c>Anregungen, Wünsche</c>
</result>


**Sentences:**
"""
