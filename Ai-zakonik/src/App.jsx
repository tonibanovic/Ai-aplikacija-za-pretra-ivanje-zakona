import Header from './Header.jsx'
import Footer from './Footer.jsx'
import Body from './Body.jsx'
import { useState, useEffect } from "react";

function App() {
  const [messages, setMessages] = useState([]);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [sessionId, setSessionId] = useState("");

  const generirajNovuSesiju = () => {
    const noviId = 'session-' + Date.now() + '-' + Math.random().toString(36).substring(2, 9);
    setSessionId(noviId);
  };

  useEffect(() => {
    generirajNovuSesiju();
  }, []);

  const handleNewChat = () =>{
    if(window.confirm("Želite li otvoriti novi razgovor?")){
      setMessages([]);
      generirajNovuSesiju();
    }

  }; 

  const handleToggleMenu = () =>{
    setIsMenuOpen(!isMenuOpen);

  };

  return (
    <div className="app">
      <Header onNewChat={handleNewChat} onToggleMenu = {handleToggleMenu} />
      <Body
        messages={messages} 
        setMessages={setMessages}
        isMenuOpen={isMenuOpen}
        sessionId={sessionId}
      />

      <Footer />
    </div>
  );
}

export default App;
