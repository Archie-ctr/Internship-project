import Link from "next/link";

/* ─── Small inline icon components ─────────────────────────────────────────
   Plain SVG so there is no icon-library dependency. Each one is designed on
   a 24 × 24 viewBox and rendered at a fixed size via className.             */

function IconShield({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75} strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
    </svg>
  );
}
function IconDocument({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75} strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="16" y1="13" x2="8" y2="13" />
      <line x1="16" y1="17" x2="8" y2="17" />
      <polyline points="10 9 9 9 8 9" />
    </svg>
  );
}
function IconClock({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75} strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <polyline points="12 6 12 12 16 14" />
    </svg>
  );
}
function IconBell({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75} strokeLinecap="round" strokeLinejoin="round">
      <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
      <path d="M13.73 21a2 2 0 0 1-3.46 0" />
    </svg>
  );
}
function IconCheck({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}
function IconArrowRight({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
      <line x1="5" y1="12" x2="19" y2="12" />
      <polyline points="12 5 19 12 12 19" />
    </svg>
  );
}

/* ─── Data ──────────────────────────────────────────────────────────────── */

const features = [
  {
    icon: <IconShield className="h-7 w-7" />,
    title: "Secure by design",
    body: "JWT authentication, bcrypt passwords, role-based access control, and a full audit trail on every state change.",
  },
  {
    icon: <IconDocument className="h-7 w-7" />,
    title: "Document management",
    body: "Upload supporting documents with type and size validation. Officers review originals before any decision is made.",
  },
  {
    icon: <IconClock className="h-7 w-7" />,
    title: "Real-time tracking",
    body: "Watch your application move from submitted → reviewed → paid → approved. Every transition is logged and visible.",
  },
  {
    icon: <IconBell className="h-7 w-7" />,
    title: "Instant notifications",
    body: "Email and SMS alerts fire automatically when your status changes, so you never have to wonder what's happening.",
  },
];

const steps = [
  { number: "01", title: "Create an account", body: "Register in under a minute with your email address." },
  { number: "02", title: "Choose a service", body: "Browse the catalogue and select the registration type you need." },
  { number: "03", title: "Fill the form", body: "Complete the guided application form and attach your documents." },
  { number: "04", title: "Pay the fee", body: "Pay the registration fee securely through the integrated payment gateway." },
  { number: "05", title: "Officer review", body: "A government officer reviews your submission and makes a decision." },
  { number: "06", title: "Receive your certificate", body: "Download your official digital certificate once approved." },
];

const stats = [
  { value: "< 5 min", label: "to submit an application" },
  { value: "100%", label: "paperless process" },
  { value: "24 / 7", label: "online availability" },
  { value: "Secure", label: "end-to-end encryption" },
];

/* ─── Page ──────────────────────────────────────────────────────────────── */

export default function HomePage() {
  return (
    <>
      {/* ── Hero ──────────────────────────────────────────────────────────── */}
      <section className="relative overflow-hidden bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 px-6 py-28 text-white sm:py-40">
        {/* Decorative blurred circles */}
        <div
          aria-hidden
          className="pointer-events-none absolute -top-40 left-1/2 h-[600px] w-[600px] -translate-x-1/2 rounded-full bg-blue-600 opacity-10 blur-3xl"
        />
        <div
          aria-hidden
          className="pointer-events-none absolute -bottom-32 right-0 h-[400px] w-[400px] rounded-full bg-indigo-500 opacity-10 blur-3xl"
        />

        <div className="relative mx-auto max-w-4xl text-center">
          <span className="inline-block rounded-full border border-blue-400/30 bg-blue-500/10 px-4 py-1.5 text-sm font-medium text-blue-300">
            Digital Public Services · Rwanda
          </span>

          <h1 className="mt-6 text-4xl font-bold leading-tight tracking-tight sm:text-6xl">
            Register your business{" "}
            <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              fully online
            </span>
          </h1>

          <p className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-slate-300">
            BizReg is a secure, end-to-end digital service for business registration. Submit
            your application, upload documents, pay fees, and receive your official
            certificate — without visiting a government office.
          </p>

          <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Link
              href="/register"
              className="flex items-center gap-2 rounded-lg bg-blue-600 px-7 py-3.5 font-semibold text-white shadow-lg shadow-blue-900/40 transition hover:bg-blue-500 hover:shadow-blue-800/50"
            >
              Start your application
              <IconArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="/services"
              className="rounded-lg border border-white/20 bg-white/5 px-7 py-3.5 font-semibold text-white backdrop-blur transition hover:bg-white/10"
            >
              Browse services
            </Link>
          </div>

          {/* Social proof strip */}
          <div className="mt-16 flex flex-wrap items-center justify-center gap-6 text-sm text-slate-400">
            {["No paperwork", "Instant status updates", "Official digital certificates", "Secure payments"].map(
              (item) => (
                <span key={item} className="flex items-center gap-1.5">
                  <IconCheck className="h-4 w-4 text-emerald-400" />
                  {item}
                </span>
              )
            )}
          </div>
        </div>
      </section>

      {/* ── Stats bar ─────────────────────────────────────────────────────── */}
      <section className="border-y border-slate-200 bg-white">
        <div className="mx-auto grid max-w-5xl grid-cols-2 divide-x divide-y divide-slate-100 sm:grid-cols-4 sm:divide-y-0">
          {stats.map((s) => (
            <div key={s.label} className="px-8 py-8 text-center">
              <p className="text-3xl font-bold text-blue-700">{s.value}</p>
              <p className="mt-1 text-sm text-slate-500">{s.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Features ──────────────────────────────────────────────────────── */}
      <section className="bg-slate-50 px-6 py-24">
        <div className="mx-auto max-w-5xl">
          <div className="text-center">
            <p className="text-sm font-semibold uppercase tracking-widest text-blue-600">
              Why BizReg
            </p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
              Built for citizens. Designed for trust.
            </h2>
            <p className="mx-auto mt-4 max-w-2xl text-slate-500">
              Every part of the platform is designed around security, transparency, and
              ease of use — so you can focus on your business, not on bureaucracy.
            </p>
          </div>

          <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {features.map((f) => (
              <div
                key={f.title}
                className="group rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:border-blue-200 hover:shadow-md"
              >
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50 text-blue-600 transition group-hover:bg-blue-100">
                  {f.icon}
                </div>
                <h3 className="mt-5 font-semibold text-slate-900">{f.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-500">{f.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── How it works ──────────────────────────────────────────────────── */}
      <section className="bg-white px-6 py-24">
        <div className="mx-auto max-w-5xl">
          <div className="text-center">
            <p className="text-sm font-semibold uppercase tracking-widest text-blue-600">
              The process
            </p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
              Six steps from start to certificate
            </h2>
          </div>

          <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {steps.map((step) => (
              <div
                key={step.number}
                className="relative rounded-2xl border border-slate-100 bg-slate-50 p-6"
              >
                <span className="text-5xl font-black tracking-tighter text-slate-100 select-none">
                  {step.number}
                </span>
                <h3 className="mt-2 font-semibold text-slate-900">{step.title}</h3>
                <p className="mt-1.5 text-sm leading-relaxed text-slate-500">{step.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA banner ────────────────────────────────────────────────────── */}
      <section className="bg-gradient-to-r from-blue-700 to-blue-600 px-6 py-20 text-white">
        <div className="mx-auto max-w-3xl text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Ready to register your business?
          </h2>
          <p className="mt-4 text-blue-100">
            Create a free account in seconds. No paperwork, no queues, no wasted trips.
          </p>
          <div className="mt-8 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Link
              href="/register"
              className="flex items-center gap-2 rounded-lg bg-white px-7 py-3.5 font-semibold text-blue-700 shadow transition hover:bg-blue-50"
            >
              Get started for free
              <IconArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="/login"
              className="rounded-lg border border-blue-400/40 bg-blue-600/40 px-7 py-3.5 font-semibold text-white transition hover:bg-blue-600/60"
            >
              Sign in to existing account
            </Link>
          </div>
        </div>
      </section>
    </>
  );
}
