import asyncio
import edge_tts
import PyPDF2

# Step 1: Convert PDF to Text and Replace '\n' with '<break time="0s"/>'
def pdf_to_text(pdf_file):
    with open(pdf_file, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
    
    # Replace all newline characters with <break time="0s"/>
    text = text.replace('\n', '')
    
    return text

# Step 2: Convert Text to Speech Using edge_tts
async def text_to_speech(text, voice, output_file='output.mp3', rate='-10%'):
    print(f"Selected voice: {voice}")  # Log the selected voice for debugging
    # Creating communicator with correct parameters
    communicator = edge_tts.Communicate(text, voice, rate=rate)
    
    # Save audio output to file
    await communicator.save(output_file)
    print(f"Speech saved to {output_file}")

# Main function
async def main():
    # Prompt the user for the language input
    language = input("Enter language code ('en' for English, 'ar' for Arabic): ").strip().lower()
    
    # Choose voice based on the selected language
    if language == 'en':
        voice = 'en-US-ChristopherNeural'  # English voicear
    elif language == 'ar':
        voice = 'ar-IQ-BasselNeural'  # Arabic voice
    else:
        print("Invalid language code. Defaulting to English.")
        voice = 'en-US-ChristopherNeural'  # Default to English voice
    
    # Extract text from the PDF
    pdf_file = r'C:\Users\cukur\Downloads\ktab.pdf'
    text = pdf_to_text(pdf_file)
    print(f"Text extracted from PDF: {text[:500]}...")  # Print first 500 characters for preview
    
    # Convert the extracted text to speech with controlled speed
    await text_to_speech(text, voice=voice)  # Use '0.7' for slower speech speed

# Run the asyncio event loop
if __name__ == '__main__':
    asyncio.run(main())
