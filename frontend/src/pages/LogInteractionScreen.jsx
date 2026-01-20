import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { updateForm, addChatMessage, setLoading } from '../redux/slices/interactionSlide';
import axios from 'axios';

const LogInteractionScreen = () => {
  const dispatch = useDispatch();
  const { formData, chatMessages, loading } = useSelector((state) => state.interaction);

  const [chatInput, setChatInput] = useState('');

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    dispatch(updateForm({ [name]: value }));
  };

  const handleSentimentChange = (e) => {
    dispatch(updateForm({ sentiment: e.target.value }));
  };

  const handleChatSend = async () => {
    if (!chatInput.trim()) return;

    const userMsg = { role: 'user', content: chatInput };
    dispatch(addChatMessage(userMsg));
    dispatch(setLoading(true));

    try {
      const response = await axios.post('http://localhost:8000/chat', { message: chatInput });
      const { reply, extracted_data } = response.data;

      console.log('Backend response:', response.data); // Debug - remove before video

      const aiMsg = { role: 'assistant', content: reply };
      dispatch(addChatMessage(aiMsg));

      // Auto-fill: snake_case → camelCase mapping (full coverage including summary)
      if (extracted_data && Object.keys(extracted_data).length > 0) {
        console.log('Raw extracted_data from backend:', extracted_data);

        const normalizedData = {};

        if (extracted_data.hcp_name) normalizedData.hcpName = extracted_data.hcp_name;
        if (extracted_data.attendees) normalizedData.attendees = extracted_data.attendees;
        if (extracted_data.date) normalizedData.date = extracted_data.date;
        if (extracted_data.time) normalizedData.time = extracted_data.time;
        if (extracted_data.interaction_type) normalizedData.interactionType = extracted_data.interaction_type;
        if (extracted_data.topics) normalizedData.topics = extracted_data.topics;
        if (extracted_data.materials_distributed) normalizedData.materialsDistributed = extracted_data.materials_distributed;
        if (extracted_data.outcomes) {
          normalizedData.outcomes = extracted_data.outcomes;
          normalizedData.sentiment = extracted_data.outcomes; // sync sentiment with outcome
        }
        if (extracted_data.follow_up) normalizedData.followUp = extracted_data.follow_up;
        if (extracted_data.summary) normalizedData.summary = extracted_data.summary;

        console.log('Normalized data for form:', normalizedData);
        dispatch(updateForm(normalizedData));
      } else {
        console.log('No extracted_data received');
      }
    } catch (error) {
      console.error('API Error:', error.response?.data || error.message);
      dispatch(addChatMessage({
        role: 'assistant',
        content: `Error: ${error.response?.data?.error || 'Could not connect to AI assistant.'}`
      }));
    }

    dispatch(setLoading(false));
    setChatInput('');
  };

  return (
    <div style={{
      display: 'flex',
      height: '100vh',
      background: '#f8f9fc',
      fontFamily: "'Inter', sans-serif",
      padding: '20px',
      gap: '20px',
      overflow: 'hidden'
    }}>
      {/* Left: Log HCP Interaction Form */}
      <div style={{
        flex: 1,
        background: '#fff',
        borderRadius: '12px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
        padding: '24px 32px',
        overflowY: 'auto'
      }}>
        <h2 style={{ margin: '0 0 24px 0', fontSize: '26px', color: '#1a1f36', fontWeight: 600 }}>
          Log HCP Interaction
        </h2>

        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500, color: '#1a1f36' }}>
            HCP Name
          </label>
          <input
            name="hcpName"
            placeholder="Search or select HCP..."
            value={formData.hcpName || ''}
            onChange={handleFormChange}
            style={{
              width: '100%',
              padding: '12px',
              border: '1px solid #d1d5db',
              borderRadius: '6px',
              fontSize: '14px'
            }}
          />
        </div>

        <div style={{ display: 'flex', gap: '16px', marginBottom: '24px' }}>
          <div style={{ flex: 1 }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500, color: '#1a1f36' }}>
              Date
            </label>
            <input
              type="date"
              name="date"
              value={formData.date || ''}
              onChange={handleFormChange}
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #d1d5db',
                borderRadius: '6px'
              }}
            />
          </div>
          <div style={{ flex: 1 }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500, color: '#1a1f36' }}>
              Time
            </label>
            <input
              type="time"
              name="time"
              value={formData.time || ''}
              onChange={handleFormChange}
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #d1d5db',
                borderRadius: '6px'
              }}
            />
          </div>
        </div>

        <div style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500, color: '#1a1f36' }}>
              Interaction Type
            </label>
            <select
              name="interactionType"
              value={formData.interactionType || 'Meeting'}
              onChange={handleFormChange}
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                background: '#fff'
              }}
            >
              <option value="Meeting">Meeting</option>
              <option value="Call">Call</option>
              <option value="Email">Email</option>
              <option value="Virtual">Virtual</option>
            </select>
          </div>

        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500, color: '#1a1f36' }}>
            Attendees
          </label>
          <input
            name="attendees"
            placeholder="Enter names or search..."
            value={formData.attendees || ''}
            onChange={handleFormChange}
            style={{
              width: '100%',
              padding: '12px',
              border: '1px solid #d1d5db',
              borderRadius: '6px'
            }}
          />
        </div>

        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500, color: '#1a1f36' }}>
            Topics Discussed
          </label>
          <textarea
            name="topics"
            placeholder="Enter key discussion points..."
            value={formData.topics || ''}
            onChange={handleFormChange}
            rows={4}
            style={{
              width: '100%',
              padding: '12px',
              border: '1px solid #d1d5db',
              borderRadius: '6px',
              resize: 'vertical'
            }}
          />
        </div>

        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500, color: '#1a1f36' }}>
            Materials Shared / Samples Distributed
          </label>
          <div style={{ marginBottom: '12px' }}>
            <strong style={{ fontSize: '14px', color: '#4b5563' }}>Materials Shared</strong>
            <div style={{ display: 'flex', gap: '12px', marginTop: '8px' }}>
              <button style={{
                padding: '8px 16px',
                background: '#f0f4ff',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                color: '#3b82f6',
                fontSize: '14px'
              }}>
                Search/Add
              </button>
              <span style={{ color: '#6b7280', fontSize: '14px' }}>
                {formData.materialsDistributed || 'No materials added.'}
              </span>
            </div>
          </div>

        </div>

        {/* Combined HCP Sentiment & Outcomes */}
        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500, color: '#1a1f36' }}>
            HCP Sentiment & Outcomes
          </label>
          <div style={{ display: 'flex', gap: '32px', marginBottom: '12px', flexWrap: 'wrap' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
              <input
                type="radio"
                name="sentiment"
                value="Positive"
                checked={formData.sentiment === 'Positive'}
                onChange={handleSentimentChange}
                readOnly={true} // Prevent manual change after auto-fill
                style={{ cursor: 'default', accentColor: '#10b981' }}
              />
              <span style={{ fontSize: '24px' }}>😊</span> Positive
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
              <input
                type="radio"
                name="sentiment"
                value="Neutral"
                checked={formData.sentiment === 'Neutral' || !formData.sentiment}
                onChange={handleSentimentChange}
                readOnly={true}
                style={{ cursor: 'default', accentColor: '#eab308' }}
              />
              <span style={{ fontSize: '24px' }}>😐</span> Neutral
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
              <input
                type="radio"
                name="sentiment"
                value="Negative"
                checked={formData.sentiment === 'Negative'}
                onChange={handleSentimentChange}
                readOnly={true}
                style={{ cursor: 'default', accentColor: '#ef4444' }}
              />
              <span style={{ fontSize: '24px' }}>😔</span> Negative
            </label>
          </div>
          <textarea
            name="outcomes"
            placeholder="Key outcomes or agreements..."
            value={formData.outcomes || ''}
            onChange={handleFormChange}
            rows={3}
            style={{
              width: '100%',
              padding: '12px',
              border: '1px solid #d1d5db',
              borderRadius: '6px',
              marginTop: '12px'
            }}
          />
        </div>

        {/* Summary field - now utilizing the backend summary */}
        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500, color: '#1a1f36' }}>
            AI Generated Summary
          </label>
          <textarea
            name="summary"
            value={formData.summary || ''}
            readOnly
            rows={4}
            style={{
              width: '100%',
              padding: '12px',
              border: '1px solid #d1d5db',
              borderRadius: '6px',
              background: '#f8f9fa',
              color: '#374151',
              resize: 'vertical'
            }}
            placeholder="AI-generated summary will appear here..."
          />
        </div>

        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500, color: '#1a1f36' }}>
            Follow-up Actions
          </label>
          <textarea
            name="followUp"
            placeholder="Enter next steps or tasks..."
            value={formData.followUp || ''}
            onChange={handleFormChange}
            rows={3}
            style={{
              width: '100%',
              padding: '12px',
              border: '1px solid #d1d5db',
              borderRadius: '6px'
            }}
          />
          <div style={{ marginTop: '8px', color: '#4b5563', fontSize: '14px' }}>
            AI Suggested Follow-ups:
            <ul style={{ margin: '4px 0 0 20px', padding: 0, listStyleType: 'disc' }}>
              <li>Schedule follow-up meeting in 2 weeks</li>
              <li>Send product samples</li>
            </ul>
          </div>
        </div>

        <button
          type="submit"
          style={{
            padding: '12px 32px',
            background: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            fontSize: '16px',
            cursor: 'pointer',
            width: '100%',
            marginTop: '16px'
          }}
        >
          Log
        </button>
      </div>

      {/* Right: AI Assistant */}
      <div style={{
        flex: 1,
        background: '#fff',
        borderRadius: '12px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
        padding: '24px',
        display: 'flex',
        flexDirection: 'column'
      }}>
        <h2 style={{ margin: '0 0 16px 0', fontSize: '20px', color: '#1a1f36' }}>
          AI Assistant
        </h2>
        <div style={{
          flex: 1,
          overflowY: 'auto',
          border: '1px solid #e5e7eb',
          borderRadius: '8px',
          padding: '16px',
          background: '#f9fafb',
          marginBottom: '16px'
        }}>
          {chatMessages.length === 0 && (
            <div style={{ color: '#6b7280', fontSize: '14px', lineHeight: '1.5' }}>
              Log interaction details here via chat (e.g., "Met Dr. Smith, discussed Product X efficacy, positive outcome, shared brochure") or ask for help.
            </div>
          )}
          {chatMessages.map((msg, idx) => (
            <div key={idx} style={{
              marginBottom: '16px',
              textAlign: msg.role === 'user' ? 'right' : 'left'
            }}>
              <strong style={{ color: msg.role === 'user' ? '#2563eb' : '#374151' }}>
                {msg.role === 'user' ? 'You' : 'AI Assistant'}:
              </strong>
              <div style={{
                marginTop: '6px',
                padding: '12px',
                borderRadius: '12px',
                background: msg.role === 'user' ? '#dbeafe' : '#ffffff',
                border: msg.role === 'user' ? 'none' : '1px solid #e5e7eb',
                display: 'inline-block',
                maxWidth: '90%'
              }}>
                {msg.content}
              </div>
            </div>
          ))}
          {loading && <div style={{ textAlign: 'center', color: '#6b7280' }}>Thinking...</div>}
        </div>

        <div style={{ marginTop: '16px', display: 'flex', gap: '12px' }}>
          <textarea
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            placeholder="Describe interaction..."
            style={{
              flex: 1,
              minHeight: '80px',
              padding: '12px',
              border: '1px solid #d1d5db',
              borderRadius: '6px',
              fontSize: '14px',
              resize: 'vertical'
            }}
          />
          <button
            onClick={handleChatSend}
            disabled={loading}
            style={{
              padding: '12px 24px',
              background: '#10b981',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              fontSize: '14px',
              cursor: loading ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            Log
          </button>
        </div>
      </div>
    </div>
  );
};

export default LogInteractionScreen;