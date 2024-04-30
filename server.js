// node --version # Should be >= 18
// npm install @google/generative-ai express

const express = require('express');
const { GoogleGenerativeAI, HarmCategory, HarmBlockThreshold } = require('@google/generative-ai');
const dotenv = require('dotenv').config()

const app = express();
const port = process.env.PORT || 3000;
app.use(express.json());
const MODEL_NAME = "gemini-pro";
const API_KEY = process.env.AIzaSyD9DsoLYpqQ_kw5OFIbL3fB2vXHFq3uA2c;

const fs = require('fs');

// Function to log chats to a file
function logChat(userInput, response) {
  const logEntry = `${new Date().toISOString()}: User: ${userInput}, Bot: ${response}\n`;
  fs.appendFile('chat.log', logEntry, (err) => {
    if (err) {
      console.error('Error logging chat:', err);
    }
  });
}

async function runChat(userInput) {
  const genAI = new GoogleGenerativeAI('AIzaSyD9DsoLYpqQ_kw5OFIbL3fB2vXHFq3uA2c');
  const model = genAI.getGenerativeModel({ model: MODEL_NAME });

  const generationConfig = {
    temperature: 0.9,
    topK: 1,
    topP: 1,
    maxOutputTokens: 1000,
  };

  const safetySettings = [
    {
      category: HarmCategory.HARM_CATEGORY_HARASSMENT,
      threshold: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    },
    // ... other safety settings
  ];

  const chat = model.startChat({
    generationConfig,
    safetySettings,
    history: [
      {
        role: "user",
        parts: [{ text: "You are question asking complaint registering chatbot, you have to ask one relevent question in accordance to the crime occurred with him or her. You have to ask different type of questions regarding incident one by one. Dont ask all at once. Here is sample example how to behave -"}],
      },
      {
        role: "model",
        parts: [{ text: "Hello! Welcome to FIR Bot. My name is FIR-SAHAYAK. Can you please provide a detailed account of the incident?"}],
      },
      {
        role: "user",
        parts: [{ text: "Yes, I was waiting for the bus, and suddenly someone snatched my bag, and my phone was stolen."}],
      },
      {
        role: "model",
        parts: [{ text: " I'm sorry to hear that. Can you provide me with some details about the location where the incident occurred?"}],
      },

      {
        role: "user",
        parts: [{ text: "It happened at the bus stop near my college campus, on Oak Street."}],
      },
      {
        role: "model",
        parts: [{ text: "Thank you. Was there anyone else around when the theft occurred?"}],
      }, {
        role: "user",
        parts: [{ text: "There were a few other people waiting for the bus, but I didn't notice anyone suspicious."}],
      },
      {
        role: "model",
        parts: [{ text: "Understood. Did you see anyone acting strangely or notice any suspicious behavior before or after the theft?"}],
      }, {
        role: "user",
        parts: [{ text: " No, everything seemed normal until it happened."}],
      },
      {
        role: "model",
        parts: [{ text: "Okay. Could you please describe your mobile phone? What brand and model is it?"}],
      }, {
        role: "user",
        parts: [{ text: "It's an iPhone XS, silver color, with a black phone case."}],
      },
      {
        role: "model",
        parts: [{ text: "Great. Do you remember if your phone had any distinguishing marks or features that could help us identify it?"}],
      }, {
        role: "user",
        parts: [{ text: "Yes, there's a small scratch on the back near the camera lens."}],
      },
      {
        role: "model",
        parts: [{ text: "Okay. Lastly, do you have any insurance coverage for your mobile phone?"}],
      },
      {
        role: "user",
        parts: [{ text: "No, unfortunately, I don't."}],
      },
      {
        role: "model",
        parts: [{ text: "Thank you for providing all the necessary information,. I will now proceed to generate your FIR report based on the details you've provided. Is there anything else you would like to add before we finalize the report?"}],
      },
      {
        role: "user",
        parts: [{ text: "No, that's all."}],
      },
      {
        role: "model",
        parts: [{ text: " Alright. Your FIR report has been successfully generated and submitted. You will receive a copy of it via email for your records. If you have any further questions or updates regarding your case, please don't hesitate to contact us. Thank you for using the FIR Register Portal chatbot."}],
      },
    ],
  });

  const result = await chat.sendMessage(userInput);
  const response = result.response;
  return response.text();
}

app.get('/', (req, res) => {
  res.sendFile(__dirname + '/index_bot.html');
});
app.get('/loader.gif', (req, res) => {
  res.sendFile(__dirname + '/loader.gif');
});
app.post('/chat', async (req, res) => {
  try {
    const userInput = req.body?.userInput;
    console.log('incoming /chat req', userInput)
    if (!userInput) {
      return res.status(400).json({ error: 'Invalid request body' });
    }

    const response = await runChat(userInput);
    
    // Log the incoming and outgoing chats
    logChat(userInput, response);
    
    res.json({ response });
  } catch (error) {
    console.error('Error in chat endpoint:', error);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});
function logChat(userInput, response) {
  const logEntry = `${new Date().toISOString()}: User: ${userInput}, Bot: ${response}\n`;
  fs.appendFile('chat.txt', logEntry, (err) => {
    if (err) {
      console.error('Error logging chat:', err);
    }
  });
}

app.listen(port, () => {
  console.log(`Server listening on port ${port}`);
});
