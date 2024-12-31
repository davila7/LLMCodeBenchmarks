import React, { useState } from 'react';
import './ContactForm';

const ContactForm = () => {
  // State hooks to manage form inputs and submission status
  const [name,Name] = useState('');
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [submitted, setSubmitted] = useState(false);

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();

    // Check if all fields are filled
    if (name && email && message) {
      // Clear form fields
      setName('');
      setEmail('');
      setMessage('');
      // Set submission status to true
      setSubmitted(true);
    }
  };

  return (
    <div className="contact-form-container">
      <h2>Contact Us</h2>
      {submitted ? (
        // Display thank you message if form is submitted
        <p>Thank you for your message. We will get back to you soon.</p>
      ) : (
        // Render form if not submitted
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">Name</label>
            <input
              type="text"
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="message">Message</label>
            <textarea
              id="message"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              required
            />
          </div>
          <button type="submit">Submit</button>
        </form>
      )}
    </div>
  );
};
