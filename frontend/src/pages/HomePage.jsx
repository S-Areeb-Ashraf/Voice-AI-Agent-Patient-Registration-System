import React from 'react';
import {
  IconMic,
  IconUsers,
  IconBolt,
  IconShield,
  IconClock,
  IconChat,
  IconPhone,
  IconSpark,
  IconLock,
  IconHealth,
  IconArrow,
} from '../components/Icons';

/**
 * Home / landing page — describes Care Cloud AI, the Voice-AI
 * phone receptionist that registers patients automatically.
 */
export default function HomePage({ onOpenDashboard, onOpenPatients }) {
  const features = [
    {
      icon: <IconPhone size={20} />,
      title: 'Natural Phone Conversations',
      text: 'A warm AI receptionist powered by Vapi and Google Gemini talks to patients like a human — collecting names, DOB, address and insurance in a smooth back-and-forth.',
    },
    {
      icon: <IconBolt size={20} />,
      title: 'Real-Time Registration',
      text: 'Mid-call tools validate every field server-side and write verified records straight into Supabase Postgres — the patient finishes the call fully registered.',
    },
    {
      icon: <IconUsers size={20} />,
      title: 'Smart Duplicate Detection',
      text: 'Returning patients are recognised by their phone number in seconds, greeted by name, and offered an update flow instead of a duplicate record.',
    },
    {
      icon: <IconChat size={20} />,
      title: 'Every Word, Saved',
      text: 'Call summaries and the full AI-vs-patient script are stored turn by turn, reviewable in a clean chat timeline from the dashboard.',
    },
    {
      icon: <IconShield size={20} />,
      title: 'Strict Clinical Validation',
      text: '10-digit phones, 2-letter states, ZIP+4 codes, future-proof DOB checks. Bad data is re-prompted in conversation — never silently stored.',
    },
    {
      icon: <IconClock size={20} />,
      title: '24/7 Availability',
      text: 'No hold music, no office hours. Your clinic takes intake calls around the clock, every day, without adding staffing cost.',
    },
  ];

  const steps = [
    { n: '01', title: 'Patient calls in', text: 'The Vapi voice agent answers with a friendly greeting and starts the intake conversation.' },
    { n: '02', title: 'AI collects & verifies', text: 'Details are gathered conversationally, validated server-side, and confirmed with the patient before saving.' },
    { n: '03', title: 'Record lands instantly', text: 'The verified patient row is written to your database, plus the transcript and per-turn script for review.' },
  ];

  return (
    <div className="home-page">
      {/* ── Hero ── */}
      <section className="home-hero">
        <div className="home-hero-left">
          <span className="home-eyebrow">
            <IconSpark size={13} />
            Voice AI for clinics
          </span>
          <h1 className="home-headline">
            Your clinic's <span className="grad-text">AI receptionist</span> on every phone call
          </h1>
          <p className="home-lede">
            Care Cloud AI is a voice-first patient intake system. A natural, empathetic
            voice agent answers the phone, registers and updates patients, validates
            every detail, and files clean records and full transcripts — while your
            staff focus on care, not data entry.
          </p>
          <div className="home-cta-row">
            <button className="btn btn-primary btn-lg" onClick={onOpenDashboard}>
              Open Dashboard <IconArrow size={15} />
            </button>
            <button className="btn btn-ghost btn-lg" onClick={onOpenPatients}>
              View Patient Registry
            </button>
          </div>
          <div className="home-hero-chips">
            <span className="home-chip"><IconLock size={12} /> Verified data, no hardcoding</span>
            <span className="home-chip"><IconHealth size={12} /> Built for clinical intake</span>
            <span className="home-chip"><IconClock size={12} /> Always answering</span>
          </div>
        </div>

        {/* Decorative "live call" mock */}
        <div className="home-hero-visual" aria-hidden="true">
          <div className="home-call-card">
            <div className="home-call-top">
              <span className="home-call-dot"></span>
              Live intake call
            </div>
            <div className="home-wave">
              {Array.from({ length: 18 }).map((_, i) => (
                <span key={i} style={{ animationDelay: `${(i % 9) * 0.12}s` }} />
              ))}
            </div>
            <div className="home-chat-mini">
              <div className="hm-line ai">Hi! Welcome to Care Cloud Clinic. How can I help you today?</div>
              <div className="hm-line patient">Hi, I'd like to register as a new patient.</div>
              <div className="hm-line ai">Of course! Can you spell your full name for me?</div>
              <div className="hm-line patient">Jane — J-A-N-E Doe.</div>
              <div className="hm-line ai">Perfect, Jane. You're all set — welcome aboard!</div>
            </div>
            <div className="home-call-foot">
              <span><IconMic size={12} /> Gemini LLM</span>
              <span><IconUsers size={12} /> Registered ✓</span>
            </div>
          </div>
        </div>
      </section>

      {/* ── Features ── */}
      <section className="home-section">
        <h2 className="home-section-title">What the voice agent does</h2>
        <p className="home-section-sub">Everything a front-desk intake call needs — handled by the AI, end to end.</p>
        <div className="home-feature-grid">
          {features.map((f) => (
            <div key={f.title} className="home-feature-card">
              <div className="home-feature-icon">{f.icon}</div>
              <h3>{f.title}</h3>
              <p>{f.text}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── How it works ── */}
      <section className="home-section">
        <h2 className="home-section-title">How a call works</h2>
        <p className="home-section-sub">From ring to database row in a single conversation.</p>
        <div className="home-steps">
          {steps.map((s) => (
            <div key={s.n} className="home-step-card">
              <span className="home-step-num">{s.n}</span>
              <h3>{s.title}</h3>
              <p>{s.text}</p>
            </div>
          ))}
          <div className="home-step-flow" aria-hidden="true">→</div>
        </div>
      </section>

      {/* ── Stack strip ── */}
      <section className="home-stack">
        <span>Vapi Telephony</span>
        <em>+</em>
        <span>Google Gemini</span>
        <em>+</em>
        <span>FastAPI Backend</span>
        <em>+</em>
        <span>Supabase Postgres</span>
      </section>

      {/* ── Footer CTA ── */}
      <section className="home-footer-cta">
        <h2>Ready to hear it in action?</h2>
        <p>Call your Vapi number and register your first patient in under a minute.</p>
        <button className="btn btn-primary btn-lg" onClick={onOpenDashboard}>
          Open Dashboard <IconArrow size={15} />
        </button>
      </section>
    </div>
  );
}
