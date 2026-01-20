import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Interactions = () => {
  const [interactions, setInteractions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  // State to manage the open modal/details view
  const [selectedInteraction, setSelectedInteraction] = useState(null);

  useEffect(() => {
    const fetchInteractions = async () => {
      try {
        const response = await axios.get('http://localhost:8000/interactions');
        // REVERSE THE DATA HERE: Latest entries (usually end of array) move to front
        setInteractions([...response.data].reverse());
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchInteractions();
  }, []);


  const formatDate = (d) => d ? new Date(d).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) : 'N/A';
  const formatDateTime = (d) => d ? new Date(d).toLocaleString('en-GB', { dateStyle: 'medium', timeStyle: 'short' }) : 'N/A';

  if (loading) return <div style={s.loader}>Initialising Dashboard...</div>;

  return (
    <div style={s.page}>
      {/* --- HEADER --- */}
      <div style={s.headerContainer} className="no-print">
        <h1 style={s.gradientTitle}>Engagement Logs</h1>
        <div style={s.headerBar}>
          <p style={s.description}>Centralised engagement intelligence for HCP networks.</p>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button style={s.actionBtn} onClick={() => window.print()}>Export Report (Print)</button>
            <div style={s.statsBadge}>{interactions.length} Total Entries</div>
          </div>
        </div>
      </div>

      {/* --- INTERACTION ITEMS (Clickable) --- */}
      <div style={s.grid}>
        {interactions.map((item) => (
          <div
            key={item.id}
            style={s.itemDiv}
            className="interaction-card"
            onClick={() => setSelectedInteraction(item)} // Add click handler
          >
            <div style={s.topRow}>
              <div style={s.hcpName}>{item.hcp_name}</div>
              <div style={item.interaction_type === 'Virtual' ? s.pillVirtual : s.pillPhysical}>
                {item.interaction_type}
              </div>
            </div>

            <div style={s.topicDiv}>
              <div style={s.label}>Core Discussion</div>
              <div style={s.topicText}>{item.topics}</div>
            </div>

            <div style={s.bottomRow}>
              <div style={s.metaItem}>
                <div style={s.label}>Date</div>
                <div style={s.valueText}>{formatDate(item.date)}</div>
              </div>
              <div style={s.metaItem}>
                <div style={s.label}>Outcome</div>
                <div style={s.outcomeText}>{item.outcomes || 'Pending'}</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* --- MODAL/DETAILS VIEW --- */}
      {selectedInteraction && (
        <DetailsModal
          item={selectedInteraction}
          onClose={() => setSelectedInteraction(null)}
          formatDate={formatDate}
          formatDateTime={formatDateTime}
        />
      )}

      {/* Animation and Print Styles */}
      <style>{`
        .interaction-card { transition: all 0.25s ease; cursor: pointer; }
        .interaction-card:hover { transform: translateY(-5px); box-shadow: 0 15px 30px rgba(0,0,0,0.1); border-color: #6366f1; }
        
        @media print {
          .no-print { display: none !important; }
          .interaction-card { border: 1px solid #ccc; box-shadow: none; transform: none; }
          body { background: #fff; }
        }
      `}</style>
    </div>
  );
};

// --- Details Modal Component (Separate for clarity) ---
const DetailsModal = ({ item, onClose, formatDate, formatDateTime }) => (
  <div style={s.modalOverlay} className="no-print">
    <div style={s.modalContent}>
      <header style={s.modalHeader}>
        <h2 style={s.modalTitle}>{item.hcp_name}</h2>
        <button onClick={onClose} style={s.closeBtn}>✕</button>
      </header>

      <div style={s.modalBody}>
        <div style={s.detailGroup}>
          <div style={s.label}>Attendees</div>
          <p style={s.detailText}>{item.attendees || 'None'}</p>
        </div>
        <div style={s.detailGroup}>
          <div style={s.label}>Interaction Type</div>
          <p style={s.detailText}>{item.interaction_type}</p>
        </div>
        <div style={s.detailGroup}>
          <div style={s.label}>Discussion Topics</div>
          <p style={s.detailText}>{item.topics}</p>
        </div>
        <div style={s.detailGroup}>
          <div style={s.label}>Materials Distributed</div>
          <p style={s.detailText}>{item.materials_distributed || 'None'}</p>
        </div>
        <div style={s.detailGroup}>
          <div style={s.label}>Outcomes Summary</div>
          <p style={s.detailText}>{item.outcomes || 'Pending'}</p>
        </div>

        <div style={s.modalFooter}>
          <div>
            <div style={s.label}>Created At</div>
            <p style={s.detailTextSmall}>{formatDateTime(item.created_at)}</p>
          </div>
          <div>
            <div style={s.label}>Last Updated</div>
            <p style={s.detailTextSmall}>{formatDateTime(item.updated_at || item.created_at)}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
);


const s = {
  page: { padding: '20px', maxWidth: '1250px', margin: '0 auto', fontFamily: 'sans-serif' },
  // ... (header, grid, itemDiv styles from previous code are reused) ...
  headerContainer: { marginBottom: '40px' },
  gradientTitle: { fontSize: '2.5rem', fontWeight: '900', margin: '0 0 10px 0', background: 'linear-gradient(90deg, #1e293b 0%, #6366f1 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', letterSpacing: '-0.03em' },
  headerBar: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  description: { color: '#64748b', fontSize: '1rem', margin: 0 },
  actionBtn: { background: '#0f172a', color: '#fff', border: 'none', padding: '10px 20px', borderRadius: '10px', fontSize: '0.85rem', fontWeight: '600', cursor: 'pointer' },
  statsBadge: { background: '#f1f5f9', padding: '6px 14px', borderRadius: '30px', fontSize: '0.75rem', fontWeight: 'bold', color: '#475569' },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '25px' },
  itemDiv: { background: 'rgba(255, 255, 255, 0.8)', backdropFilter: 'blur(10px)', border: '1px solid #e2e8f0', borderRadius: '24px', padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' },
  topRow: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' },
  hcpName: { fontSize: '1.25rem', fontWeight: '800', color: '#0f172a' },
  pillVirtual: { background: '#f5f3ff', color: '#7c3aed', padding: '4px 12px', borderRadius: '10px', fontSize: '0.7rem', fontWeight: 'bold', border: '1px solid #ddd6fe' },
  pillPhysical: { background: '#f0fdf4', color: '#16a34a', padding: '4px 12px', borderRadius: '10px', fontSize: '0.7rem', fontWeight: 'bold', border: '1px solid #dcfce7' },
  topicDiv: { background: '#f8fafc', padding: '16px', borderRadius: '16px', border: '1px solid #f1f5f9' },
  label: { fontSize: '0.65rem', textTransform: 'uppercase', letterSpacing: '0.1em', fontWeight: '900', color: '#94a3b8', marginBottom: '6px' },
  topicText: { fontSize: '0.9rem', color: '#334155', fontWeight: '500', lineHeight: '1.4' },
  bottomRow: { display: 'flex', borderTop: '1px solid #f1f5f9', paddingTop: '16px', justifyContent: 'space-between' },
  metaItem: { display: 'flex', flexDirection: 'column' },
  valueText: { fontSize: '0.9rem', fontWeight: '700', color: '#1e293b' },
  outcomeText: { fontSize: '0.9rem', fontWeight: '700', color: '#059669' },
  loader: { textAlign: 'center', marginTop: '100px', fontSize: '1.2rem', color: '#6366f1', fontWeight: 'bold' },

  // --- Modal Specific Styles ---
  modalOverlay: {
    position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0, 0, 0, 0.6)',
    display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000
  },
  modalContent: {
    background: '#fff', padding: '30px', borderRadius: '24px', maxWidth: '600px', width: '90%',
    boxShadow: '0 25px 50px rgba(0,0,0,0.2)', maxHeight: '90vh', overflowY: 'auto', animation: 'fadeInScale 0.3s ease-out'
  },
  modalHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #eee', paddingBottom: '20px', marginBottom: '20px' },
  modalTitle: { fontSize: '1.8rem', fontWeight: '900', color: '#1e293b' },
  closeBtn: { background: 'none', border: 'none', fontSize: '1.5rem', cursor: 'pointer', color: '#94a3b8' },
  modalBody: { display: 'flex', flexDirection: 'column', gap: '20px' },
  detailGroup: { marginBottom: '10px' },
  detailText: { fontSize: '1rem', color: '#334155', margin: '5px 0 0 0', lineHeight: '1.6' },
  detailTextSmall: { fontSize: '0.8rem', color: '#334155', margin: '5px 0 0 0' },
  modalFooter: { display: 'flex', justifyContent: 'space-between', paddingTop: '20px', borderTop: '1px solid #f1f5f9', marginTop: '20px' }
};

export default Interactions;
