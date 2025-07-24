import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>My Awesome App</h1>
        <nav>
          <a href="#home">Home</a>
          <a href="#about">About</a>
          <a href="#contact">Contact</a>
        </nav>
      </header>
      <main className="App-main">
        <div className="card">
          <h2>Welcome!</h2>
          <p>This is a starting point for a more attractive UI. You can build upon this structure.</p>
        </div>
        <div className="card">
          <h2>Next Steps</h2>
          <p>Consider using a UI component library like Material-UI or Ant Design for even faster development and a polished look.</p>
        </div>
      </main>
      <footer className="App-footer">
        <p>© 2024 My Awesome App. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;