from transformers import GPT2Tokenizer, GPT2ForSequenceClassification
import torch
from scipy.special import softmax
import numpy as np  # Adding NumPy

# Initialize the tokenizer and model with the appropriate pre-trained model name
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2ForSequenceClassification.from_pretrained('gpt2')

# Define your labels
labels = ['Positive', 'Negative']

# Define your prompt and input text
prompt = "Is the following a conversation on a radio show:"

class Classification:
    @staticmethod
    def classify(text):
        # Tokenize the prompt and input text
        prompt_encoded = tokenizer(prompt, add_special_tokens=False, return_tensors='pt')
        text_encoded = tokenizer(text, add_special_tokens=False, return_tensors='pt')

        # Combine prompt and text into a single input
        input_ids = torch.cat((prompt_encoded.input_ids, text_encoded.input_ids), dim=1)
        attention_mask = torch.cat((prompt_encoded.attention_mask, text_encoded.attention_mask), dim=1)

        # Ensure the model is in evaluation mode
        model.eval()

        # Get model outputs
        with torch.no_grad():
            outputs = model(input_ids, attention_mask=attention_mask)

        # Extract the logits
        logits = outputs.logits

        # Convert logits to probabilities
        probabilities = softmax(logits[0].cpu().numpy())

        print(f"Logits: {logits}")
        print(f"Probabilities: {probabilities}")

        # Optional: interpret the results
        predicted_label_index = np.argmax(probabilities)
        predicted_label = labels[predicted_label_index]
        return (f"Predicted label: {predicted_label} (Class {predicted_label_index})")
