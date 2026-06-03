import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  BarChart3,
  Check,
  Download,
  Eye,
  FilePlus2,
  Link,
  LogOut,
  Plus,
  Send,
  Trash2,
} from "lucide-react";
import { api, clearToken, getToken, setToken } from "./api/client";
import "./styles/app.css";

const defaultQuestion = () => ({
  code: `Q${Math.floor(Math.random() * 900 + 100)}`,
  prompt: "",
  question_type: "text",
  required: true,
  options: [],
  branch_rules: [],
});

const choiceTypes = ["radio", "checkbox", "dropdown"];

function parseOptions(value) {
  return value
    .replace(/\n/g, ",")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function Login({ onLogin }) {
  const [email, setEmail] = useState("admin@insightpro.local");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState("");

  async function submit(event) {
    event.preventDefault();
    setError("");
    try {
      const payload = await api.login({ email, password });
      setToken(payload.access_token);
      onLogin(payload);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <main className="auth-shell">
      <section className="auth-panel">
        <div>
          <p className="eyebrow">InsightPro</p>
          <h1>Customer experience survey operations</h1>
        </div>
        <form onSubmit={submit} className="stack">
          <label>
            Email
            <input value={email} onChange={(event) => setEmail(event.target.value)} />
          </label>
          <label>
            Password
            <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
          </label>
          {error && <p className="error">{error}</p>}
          <button className="primary" type="submit">
            <Check size={18} /> Sign in
          </button>
        </form>
      </section>
    </main>
  );
}

function SurveyBuilder({ onCreated }) {
  const [title, setTitle] = useState("Customer onboarding experience");
  const [description, setDescription] = useState("Measure satisfaction, effort, and follow-up risks.");
  const [customUrl, setCustomUrl] = useState("");
  const [responseMode, setResponseMode] = useState("anonymous");
  const [brandLogoUrl, setBrandLogoUrl] = useState("");
  const [brandPrimaryColor, setBrandPrimaryColor] = useState("#126b5f");
  const [brandTheme, setBrandTheme] = useState("light");
  const [defaultCountry, setDefaultCountry] = useState("");
  const [defaultProduct, setDefaultProduct] = useState("");
  const [defaultService, setDefaultService] = useState("");
  const [defaultRegion, setDefaultRegion] = useState("");
  const [questions, setQuestions] = useState([
    {
      code: "Q1",
      prompt: "How satisfied are you with your onboarding experience?",
      question_type: "rating",
      required: true,
      options: [],
      branch_rules: [{ answer: 1, go_to_code: "Q4" }, { answer: 2, go_to_code: "Q4" }],
    },
    {
      code: "Q2",
      prompt: "Which area helped you the most?",
      question_type: "radio",
      required: true,
      options: ["Training", "Support", "Documentation", "Product setup"],
      branch_rules: [],
    },
    {
      code: "Q3",
      prompt: "How likely are you to recommend us?",
      question_type: "nps",
      required: true,
      options: [],
      branch_rules: [],
    },
    {
      code: "Q4",
      prompt: "What should we improve first?",
      question_type: "text",
      required: false,
      options: [],
      branch_rules: [],
    },
  ]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  function updateQuestion(index, patch) {
    setQuestions((items) => items.map((item, itemIndex) => (itemIndex === index ? { ...item, ...patch } : item)));
  }

  async function submit(event) {
    event.preventDefault();
    setMessage("");
    setError("");
    const cleanedQuestions = questions.map((question) => ({
      ...question,
      code: question.code.trim(),
      prompt: question.prompt.trim(),
      options: choiceTypes.includes(question.question_type)
        ? question.options.map((item) => item.trim()).filter(Boolean)
        : null,
      branch_rules: question.branch_rules.filter((rule) => rule.answer !== "" && rule.go_to_code.trim()),
    }));
    const validationError = validateSurvey(title, cleanedQuestions);
    if (validationError) {
      setError(validationError);
      return;
    }
    const payload = {
      title: title.trim(),
      description: description.trim(),
      custom_url: customUrl.trim() || null,
      response_mode: responseMode,
      brand_logo_url: brandLogoUrl.trim() || null,
      brand_primary_color: brandPrimaryColor,
      brand_theme: brandTheme,
      default_country: defaultCountry.trim() || null,
      default_product: defaultProduct.trim() || null,
      default_service: defaultService.trim() || null,
      default_region: defaultRegion.trim() || null,
      questions: cleanedQuestions,
    };
    try {
      const created = await api.createSurvey(payload);
      setMessage(`Created survey ${created.title}`);
      onCreated();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="workspace-section">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Survey builder</p>
          <h2>Create a feedback program</h2>
        </div>
        <button type="button" className="ghost" onClick={() => setQuestions([...questions, defaultQuestion()])}>
          <Plus size={18} /> Question
        </button>
      </div>
      <form onSubmit={submit} className="builder-form">
        <div className="two-col">
          <label>
            Survey title
            <input value={title} onChange={(event) => setTitle(event.target.value)} />
          </label>
          <label>
            Description
            <input value={description} onChange={(event) => setDescription(event.target.value)} />
          </label>
        </div>
        <div className="enterprise-grid">
          <label>
            Custom URL slug
            <input value={customUrl} placeholder="onboarding-q2" onChange={(event) => setCustomUrl(event.target.value)} />
          </label>
          <label>
            Response mode
            <select value={responseMode} onChange={(event) => setResponseMode(event.target.value)}>
              <option value="anonymous">Anonymous</option>
              <option value="identified">Identified</option>
            </select>
          </label>
          <label>
            Logo URL
            <input value={brandLogoUrl} onChange={(event) => setBrandLogoUrl(event.target.value)} />
          </label>
          <label>
            Brand color
            <input type="color" value={brandPrimaryColor} onChange={(event) => setBrandPrimaryColor(event.target.value)} />
          </label>
          <label>
            Theme
            <select value={brandTheme} onChange={(event) => setBrandTheme(event.target.value)}>
              <option value="light">Light</option>
              <option value="contrast">Contrast</option>
            </select>
          </label>
          <label>
            Country
            <input value={defaultCountry} onChange={(event) => setDefaultCountry(event.target.value)} />
          </label>
          <label>
            Product
            <input value={defaultProduct} onChange={(event) => setDefaultProduct(event.target.value)} />
          </label>
          <label>
            Service
            <input value={defaultService} onChange={(event) => setDefaultService(event.target.value)} />
          </label>
          <label>
            Region
            <input value={defaultRegion} onChange={(event) => setDefaultRegion(event.target.value)} />
          </label>
        </div>
        <div className="question-list">
          {questions.map((question, index) => (
            <article key={`${question.code}-${index}`} className="question-row">
              <div className="question-meta">
                <input
                  aria-label="Question code"
                  value={question.code}
                  onChange={(event) => updateQuestion(index, { code: event.target.value })}
                />
                <select
                  value={question.question_type}
                  onChange={(event) => updateQuestion(index, { question_type: event.target.value })}
                >
                  <option value="text">Text</option>
                  <option value="radio">Radio</option>
                  <option value="checkbox">Checkbox</option>
                  <option value="dropdown">Dropdown</option>
                  <option value="rating">Rating</option>
                  <option value="nps">NPS</option>
                </select>
                <label className="inline-check">
                  <input
                    type="checkbox"
                    checked={question.required}
                    onChange={(event) => updateQuestion(index, { required: event.target.checked })}
                  />
                  Required
                </label>
                <button
                  title="Remove question"
                  type="button"
                  className="icon-button"
                  onClick={() => setQuestions(questions.filter((_, itemIndex) => itemIndex !== index))}
                >
                  <Trash2 size={17} />
                </button>
              </div>
              <input
                value={question.prompt}
                placeholder="Question prompt"
                onChange={(event) => updateQuestion(index, { prompt: event.target.value })}
              />
              {choiceTypes.includes(question.question_type) && (
                <label>
                  Options
                  <textarea
                    value={question.options.join(", ")}
                    onChange={(event) =>
                      updateQuestion(index, { options: parseOptions(event.target.value) })
                    }
                    rows={3}
                  />
                  <span className="hint">Use comma-separated or one option per line.</span>
                </label>
              )}
              {["rating", "nps"].includes(question.question_type) && (
                <p className="hint">
                  {question.question_type === "rating" ? "Rating answers are generated as 1 to 5." : "NPS answers are generated as 0 to 10."}
                </p>
              )}
              <div className="branch-editor">
                <span>Branch when answer equals</span>
                <input
                  value={question.branch_rules[0]?.answer ?? ""}
                  onChange={(event) =>
                    updateQuestion(index, {
                      branch_rules: [{ answer: coerceAnswer(event.target.value), go_to_code: question.branch_rules[0]?.go_to_code || "" }],
                    })
                  }
                />
                <span>go to</span>
                <input
                  value={question.branch_rules[0]?.go_to_code ?? ""}
                  onChange={(event) =>
                    updateQuestion(index, {
                      branch_rules: [{ answer: question.branch_rules[0]?.answer ?? "", go_to_code: event.target.value }],
                    })
                  }
                />
              </div>
            </article>
          ))}
        </div>
        {message && <p className="notice">{message}</p>}
        {error && <p className="error">{error}</p>}
        <button className="primary" type="submit">
          <FilePlus2 size={18} /> Create survey
        </button>
      </form>
    </section>
  );
}

function coerceAnswer(value) {
  const number = Number(value);
  return Number.isNaN(number) || value.trim() === "" ? value : number;
}

function validateSurvey(title, questions) {
  if (!title.trim()) return "Survey title is required.";
  for (const [index, question] of questions.entries()) {
    const label = question.code || `Question ${index + 1}`;
    if (!question.code) return `Question ${index + 1} needs a code.`;
    if (!question.prompt) return `${label} needs a prompt.`;
    if (choiceTypes.includes(question.question_type) && question.options.length < 2) {
      return `${label} needs at least two options.`;
    }
  }
  return "";
}

function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [tenants, setTenants] = useState([]);
  const [surveys, setSurveys] = useState([]);
  const [selectedSurveyId, setSelectedSurveyId] = useState(null);
  const [responses, setResponses] = useState([]);
  const [filters, setFilters] = useState({ country: "", product: "", service: "", region: "", date_from: "", date_to: "" });
  const [inviteEmails, setInviteEmails] = useState("");
  const [inviteMessage, setInviteMessage] = useState("");

  async function refresh() {
    const [summaryPayload, surveyPayload, tenantPayload] = await Promise.all([
      api.summary(),
      api.surveys(),
      api.tenants().catch(() => []),
    ]);
    setSummary(summaryPayload);
    setSurveys(surveyPayload);
    setTenants(tenantPayload);
    if (!selectedSurveyId && surveyPayload[0]) {
      setSelectedSurveyId(surveyPayload[0].id);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  useEffect(() => {
    if (!selectedSurveyId) return;
    api.responses(selectedSurveyId, filters).then(setResponses).catch(() => setResponses([]));
    api.analytics({ survey_id: selectedSurveyId, ...filters }).then(setAnalytics).catch(() => setAnalytics(null));
  }, [selectedSurveyId, filters]);

  async function publish(id) {
    await api.publishSurvey(id);
    await refresh();
  }

  async function downloadResponses(id, format) {
    const response = await api.exportResponses(id, format);
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `survey-${id}-responses.${format === "xlsx" ? "xls" : format === "pdf" ? "html" : "csv"}`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  async function sendInvites() {
    if (!selectedSurveyId) return;
    setInviteMessage("");
    const recipient_emails = inviteEmails.split(/[\n,]/).map((item) => item.trim()).filter(Boolean);
    const payload = await api.sendInvites({ survey_id: selectedSurveyId, recipient_emails });
    setInviteMessage(`Queued ${payload.length} invite${payload.length === 1 ? "" : "s"}.`);
    setInviteEmails("");
  }

  const selected = useMemo(() => surveys.find((survey) => survey.id === selectedSurveyId), [surveys, selectedSurveyId]);

  return (
    <>
      <section className="metrics-band">
        <Metric icon={<BarChart3 size={20} />} label="Surveys" value={summary?.surveys ?? 0} />
        <Metric icon={<Send size={20} />} label="Published" value={summary?.published ?? 0} />
        <Metric icon={<Eye size={20} />} label="Responses" value={summary?.responses ?? 0} />
        <Metric icon={<BarChart3 size={20} />} label="Avg score" value={analytics?.average_score ?? 0} />
      </section>
      {tenants.length > 0 && (
        <section className="tenant-band">
          {tenants.map((tenant) => (
            <span key={tenant.id} style={{ borderColor: tenant.primary_color }}>
              {tenant.logo_url && <img src={tenant.logo_url} alt="" />}
              {tenant.name} · {tenant.theme}
            </span>
          ))}
        </section>
      )}
      <SurveyBuilder onCreated={refresh} />
      <section className="workspace-section">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Response desk</p>
            <h2>Published links and submissions</h2>
          </div>
          {selected && (
            <div className="button-row">
              <button className="ghost" onClick={() => downloadResponses(selected.id, "csv")}>
                <Download size={18} /> CSV
              </button>
              <button className="ghost" onClick={() => downloadResponses(selected.id, "xlsx")}>
                <Download size={18} /> Excel
              </button>
              <button className="ghost" onClick={() => downloadResponses(selected.id, "pdf")}>
                <Download size={18} /> PDF
              </button>
            </div>
          )}
        </div>
        <div className="filter-grid">
          {["country", "product", "service", "region", "date_from", "date_to"].map((field) => (
            <label key={field}>
              {field}
              <input
                type={field.startsWith("date_") ? "date" : "text"}
                value={filters[field]}
                onChange={(event) => setFilters({ ...filters, [field]: event.target.value })}
              />
            </label>
          ))}
        </div>
        {analytics && (
          <div className="chart-grid">
            <MiniChart title="By region" data={analytics.by_region} />
            <MiniChart title="By product" data={analytics.by_product} />
            <MiniChart title="Score buckets" data={analytics.sentiment_buckets} />
          </div>
        )}
        <div className="response-layout">
          <div className="survey-list">
            {surveys.map((survey) => (
              <button
                key={survey.id}
                className={survey.id === selectedSurveyId ? "survey-item active" : "survey-item"}
                onClick={() => setSelectedSurveyId(survey.id)}
              >
                <strong>{survey.title}</strong>
                <span>{survey.status} · {survey.response_count} responses</span>
              </button>
            ))}
          </div>
          <div className="response-panel">
            {selected ? (
              <>
                <div className="publish-row">
                  <span className="public-link">
                    <Link size={16} /> /survey/{selected.custom_url || selected.public_slug}
                  </span>
                  {selected.status !== "published" && (
                    <button className="primary compact" onClick={() => publish(selected.id)}>
                      <Send size={16} /> Publish
                    </button>
                  )}
                </div>
                <div className="invite-panel">
                  <textarea
                    rows={3}
                    value={inviteEmails}
                    placeholder="customer@example.com, analyst@example.com"
                    onChange={(event) => setInviteEmails(event.target.value)}
                  />
                  <button className="primary compact" onClick={sendInvites}>
                    <Send size={16} /> Invite
                  </button>
                  {inviteMessage && <p className="notice">{inviteMessage}</p>}
                </div>
                <div className="responses-table">
                  {responses.length === 0 ? (
                    <p className="muted">No responses yet.</p>
                  ) : (
                    responses.map((response) => (
                      <article key={response.id} className="response-row">
                        <div>
                          <strong>{response.respondent_key.slice(0, 10)}</strong>
                          <span>{response.region || "Unassigned"} · {response.product || "No product"} · score {response.score ?? "n/a"}</span>
                          <span>{new Date(response.submitted_at).toLocaleString()}</span>
                        </div>
                        <pre>{JSON.stringify(response.answers, null, 2)}</pre>
                      </article>
                    ))
                  )}
                </div>
              </>
            ) : (
              <p className="muted">Create a survey to begin collecting responses.</p>
            )}
          </div>
        </div>
      </section>
    </>
  );
}

function MiniChart({ title, data }) {
  const entries = Object.entries(data || {});
  const max = Math.max(1, ...entries.map(([, value]) => value));
  return (
    <article className="mini-chart">
      <strong>{title}</strong>
      {entries.length === 0 ? <span className="muted">No data</span> : entries.map(([label, value]) => (
        <div key={label} className="bar-row">
          <span>{label}</span>
          <div><i style={{ width: `${(value / max) * 100}%` }} /></div>
          <b>{value}</b>
        </div>
      ))}
    </article>
  );
}

function Metric({ icon, label, value }) {
  return (
    <div className="metric">
      {icon}
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function PublicSurvey({ slug }) {
  const [payload, setPayload] = useState(null);
  const [answer, setAnswer] = useState("");
  const [done, setDone] = useState(false);
  const [error, setError] = useState("");
  const [respondentEmail, setRespondentEmail] = useState(new URLSearchParams(window.location.search).get("email") || "");
  const respondentKey = useMemo(() => localStorage.getItem(`respondent:${slug}`), [slug]);

  async function load(key = respondentKey) {
    setError("");
    try {
      const surveyPayload = await api.openPublicSurvey(slug, key);
      localStorage.setItem(`respondent:${slug}`, surveyPayload.progress.respondent_key);
      setPayload(surveyPayload);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    load();
  }, [slug]);

  const question = payload?.survey.questions.find((item) => item.code === payload.progress.current_question_code);

  async function save() {
    const progress = await api.saveAnswer(slug, {
      respondent_key: payload.progress.respondent_key,
      question_code: question.code,
      answer,
      respondent_email: respondentEmail,
    });
    setPayload({ ...payload, progress });
    setAnswer("");
  }

  async function submit() {
    await api.submitResponse(slug, { respondent_key: payload.progress.respondent_key, respondent_email: respondentEmail });
    setDone(true);
    localStorage.removeItem(`respondent:${slug}`);
  }

  if (error) {
    return (
      <main className="survey-shell">
        <section className="survey-panel">
          <h1>Survey unavailable</h1>
          <p className="error">{error}</p>
        </section>
      </main>
    );
  }
  if (!payload) return <main className="survey-shell">Loading survey...</main>;
  if (done) return <main className="survey-shell"><section className="survey-panel"><h1>Thank you</h1><p>Your feedback has been submitted.</p></section></main>;

  return (
    <main className="survey-shell">
      <section className="survey-panel">
        {payload.survey.brand_logo_url && <img className="survey-logo" src={payload.survey.brand_logo_url} alt="" />}
        <p className="eyebrow">InsightPro feedback</p>
        <h1>{payload.survey.title}</h1>
        <p>{payload.survey.description}</p>
        {payload.survey.response_mode === "identified" && (
          <label>
            Email
            <input value={respondentEmail} onChange={(event) => setRespondentEmail(event.target.value)} />
          </label>
        )}
        {question ? (
          <div className="runner">
            <span className="question-code">{question.code}</span>
            <h2>{question.prompt}</h2>
            <AnswerInput question={question} answer={answer} setAnswer={setAnswer} />
            <button className="primary" onClick={save}>
              <Check size={18} /> Save answer
            </button>
          </div>
        ) : (
          <div className="runner">
            <h2>Ready to submit</h2>
            <pre>{JSON.stringify(payload.progress.answers, null, 2)}</pre>
            <button className="primary" onClick={submit}>
              <Send size={18} /> Submit response
            </button>
          </div>
        )}
      </section>
    </main>
  );
}

function AnswerInput({ question, answer, setAnswer }) {
  if (question.question_type === "text") {
    return <textarea value={answer} onChange={(event) => setAnswer(event.target.value)} rows={5} />;
  }
  if (question.question_type === "rating") {
    return <RangeChoice max={5} answer={answer} setAnswer={setAnswer} />;
  }
  if (question.question_type === "nps") {
    return <RangeChoice max={10} answer={answer} setAnswer={setAnswer} zeroBased />;
  }
  if (question.question_type === "dropdown") {
    return (
      <select value={answer} onChange={(event) => setAnswer(event.target.value)}>
        <option value="">Select</option>
        {question.options?.map((option) => <option key={option}>{option}</option>)}
      </select>
    );
  }
  if (question.question_type === "checkbox") {
    const selected = Array.isArray(answer) ? answer : [];
    return (
      <div className="choice-grid">
        {question.options?.map((option) => (
          <label key={option} className="choice">
            <input
              type="checkbox"
              checked={selected.includes(option)}
              onChange={(event) => {
                setAnswer(event.target.checked ? [...selected, option] : selected.filter((item) => item !== option));
              }}
            />
            {option}
          </label>
        ))}
      </div>
    );
  }
  return (
    <div className="choice-grid">
      {question.options?.map((option) => (
        <label key={option} className="choice">
          <input type="radio" checked={answer === option} onChange={() => setAnswer(option)} />
          {option}
        </label>
      ))}
    </div>
  );
}

function RangeChoice({ max, answer, setAnswer, zeroBased = false }) {
  const start = zeroBased ? 0 : 1;
  return (
    <div className="score-row">
      {Array.from({ length: max - start + 1 }, (_, index) => index + start).map((score) => (
        <button
          type="button"
          className={answer === score ? "score active" : "score"}
          key={score}
          onClick={() => setAnswer(score)}
        >
          {score}
        </button>
      ))}
    </div>
  );
}

function App() {
  const [authenticated, setAuthenticated] = useState(Boolean(getToken()));
  const path = window.location.pathname;
  const publicMatch = path.match(/^\/survey\/([^/]+)/);

  if (publicMatch) return <PublicSurvey slug={publicMatch[1]} />;
  if (!authenticated) return <Login onLogin={() => setAuthenticated(true)} />;

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">InsightPro</p>
          <h1>Customer insights command center</h1>
        </div>
        <button
          className="ghost"
          onClick={() => {
            clearToken();
            setAuthenticated(false);
          }}
        >
          <LogOut size={18} /> Sign out
        </button>
      </header>
      <Dashboard />
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
