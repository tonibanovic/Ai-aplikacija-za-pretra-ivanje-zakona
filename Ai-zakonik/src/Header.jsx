import { useState } from "react";

function Header({ onNewChat, onToggleMenu}){

    return(
        <header>
            <div className = 'Header-div'>
                <img 
                    id='menu' 
                    src = 'menu.png'
                    onClick={onToggleMenu}
                ></img>
                <h1 id = 'Ai-zakonik'>AI-zakonik</h1>
                <div className = 'profile'>   
                <img 
                    id='profile' 
                    src = 'profile.png'
                    onClick = {onNewChat}
                ></img>
                </div>
            </div>
        </header>
    );
}

export default Header