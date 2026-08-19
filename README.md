# AgentPullingEcommerseceFromCSV
An ecommerce Agent is created so that it can perform below actions like 
Upload the latest CSV files for policies and FAQs
Type a natural language question
Get a clear answer that they can copy paste into an email or chat
ou will use sample CSV files - Click here to Download
Target users

● Customer support agents

● Product managers who want to test how clear their policy text is

● Operations staff who need quick answers while talking to customers on phone or chat

Data sources

● ecommerce_faqs.csv - frequently asked questions for an online store

● credit_card_terms.csv - terms and conditions for credit cards

● hospital_policy.csv - hospital rules for visits, records, and other items

● saas_docs.csv - features, limits, and support details for a software as a service product
app should cover the following points.

1. File upload

The user can upload one or many CSV files from their local machine The app shows a small preview of each file, for example the first few rows

2. Question input

The user can type a question in a text box in normal language Example questions

■ What is the return policy for electronics

■ What does the extended warranty cover

■ What are the visiting hours in the hospital

■ What is the API rate limit for the free plan

The AI must read the CSV data and find the most relevant row or rows ○ For text questions it should return the key piece of text, for example from the Answer or Policy column ○ For numeric questions it should compute totals or averages if needed ○ The answer should be in clear English, ready to share with a customer