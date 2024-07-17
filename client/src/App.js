import { useState, useEffect } from "react";
import './App.css';

const App = () => {
  const [value, setValue] = useState(null);
  const [message, setMessage] = useState(null);
  const [chatId, setChatId] = useState(1);
  const [previousChats, setPreviousChats] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Send POST request to reset threads_db when the component is mounted
    fetch('http://localhost:5000/api/reset_threads', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    .then(response => response.json())
    .then(data => {
      console.log(data.message);
    })
    .catch(error => {
      console.error('There was an error resetting the threads database!', error);
    });
  }, []);

  const createNewChat = () => {
    setValue("");
    setCurrentChatId(null);
  };

  const handleClick = (id) => {
    setCurrentChatId(id);
    setValue("");
  };

  const getMessages = async () => {
    const options = {
      method: "POST",
      body: JSON.stringify({
        message: value,
        id: !currentChatId ? String(chatId) : String(currentChatId)
      }),
      headers: {
        "Content-Type": "application/json"
      }
    };
    try {
      const response = await fetch("http://localhost:5000/api/assistant", options);
      const data = await response.json();
      setMessage(data.response);
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false); // Stop loading after receiving response or encountering error
    }
  };

  useEffect(() => {
    console.log(currentChatId, value, message);
    if (value && message) {
      if (!currentChatId) {
        setPreviousChats(prevChats => [
          ...prevChats,
          {
            chatId: chatId,
            role: "user",
            content: value,
            title: value
          },
          {
            chatId: chatId,
            role: "assistant",
            content: message,
            title: value
          }
        ]);
        setCurrentChatId(chatId);
        setChatId(chatId + 1);
      } else {
        setPreviousChats(prevChats => [
          ...prevChats,
          {
            chatId: currentChatId,
            role: "user",
            content: value,
            title: prevChats.find(chat => chat.chatId === currentChatId)?.title
          },
          {
            chatId: currentChatId,
            role: "assistant",
            content: message,
            title: prevChats.find(chat => chat.chatId === currentChatId)?.title
          }
        ]);
      }
      setValue("");
      setMessage(null);
    }
  }, [message, currentChatId, value, chatId]);

  const currentChat = previousChats.filter(chat => chat.chatId === currentChatId);
  const uniqueChats = Array.from(new Set(previousChats.map(chat => chat.chatId)))
    .map(id => ({
      id,
      title: previousChats.find(chat => chat.chatId === id)?.title
    }));

  const formatMessage = (content) => {
    const formattedContent = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    return { __html: formattedContent };
  };

  return (
    <div className="app">
      <section className="side-bar">
        <button onClick={() => {
                if (!isLoading) {
                  createNewChat();
                }
              }}>+ New chat</button>
        <ul className="history">
          {uniqueChats.map(({ id, title }) => (
            <li key={id}
              onClick={() => {
                if (!isLoading) {
                  handleClick(id);
                }
              }}
              className={id === currentChatId ? 'active' : ''}
            >
              <i className="chatIcon"></i>
              <p>{title || `Chat ${id}`}</p>
            </li>
          ))}
        </ul>
        <nav>
          <p>Made by Zion Ochayon</p>
        </nav>
      </section>
      <section className="main">
        <h1>Conversational agent for customer support queries</h1>
        <ul className="feed">
          {currentChat?.map((chatMessage, index) => (
            <li className={chatMessage.role} key={index}>
              <i className="assistantIcon" id={chatMessage.role}></i>
              <p className="formatted-message" dangerouslySetInnerHTML={formatMessage(chatMessage.content)}></p>
            </li>
          ))}
        </ul>
        <div className="bottom-section">
          <div className="input-container">
            <input value={value || ""}
              onChange={(e) => setValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !isLoading && value) {
                  setIsLoading(true);
                  getMessages();
                  e.preventDefault();
                }
              }}
              disabled={isLoading}
            />
            <div className="submit"
              onClick={() => {
                if (!isLoading && value) {
                  setIsLoading(true);
                  getMessages();
                }
              }}
              disabled={isLoading}>
              <i className={isLoading ? 'loading-state send' : 'send'}></i></div>
          </div>
          <p className="info">
            Feel free to ask anything about our store, services, and information
          </p>
        </div>
      </section>
    </div>
  );
}

export default App;
