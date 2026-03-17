import { useEffect, useState } from "react";
import {
  crearCurso,
  getMisCursos,
  getProfesores,
  getTodosLosCursos,
  inscribirseEnCurso,
  login,
  registroEstudiante,
  registroProfesor,
} from "./api";

const STORAGE_KEY = "gestion-cursos-session";

const initialLogin = {
  email: "",
  contrasenia: "",
};

const initialRegistro = {
  nombre: "",
  email: "",
  password: "",
};

const initialCurso = {
  titulo: "",
  descripcion: "",
};

function readStoredSession() {
  const raw = localStorage.getItem(STORAGE_KEY);
  return raw ? JSON.parse(raw) : null;
}

function App() {
  const [session, setSession] = useState(() => readStoredSession());
  const [loginForm, setLoginForm] = useState(initialLogin);
  const [registroProfesorForm, setRegistroProfesorForm] = useState(initialRegistro);
  const [registroEstudianteForm, setRegistroEstudianteForm] = useState(initialRegistro);
  const [cursoForm, setCursoForm] = useState(initialCurso);
  const [panel, setPanel] = useState({
    profesores: [],
    cursos: [],
    todosLosCursos: [],
  });
  const [feedback, setFeedback] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!session?.token) {
      setPanel({ profesores: [], cursos: [], todosLosCursos: [] });
      return;
    }

    loadDashboard(session);
  }, [session]);

  async function loadDashboard(activeSession = session) {
    if (!activeSession?.token) {
      return;
    }

    try {
      setLoading(true);
      setFeedback("");

      const [profesores, cursos] = await Promise.all([
        getProfesores(activeSession.token),
        getMisCursos(activeSession.token),
      ]);

      if (activeSession.rol === "estudiante") {
        const todosLosCursos = await getTodosLosCursos(activeSession.token);
        setPanel({ profesores, cursos, todosLosCursos });
      } else {
        setPanel({ profesores, cursos, todosLosCursos: [] });
      }
    } catch (error) {
      setFeedback(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleLogin(event) {
    event.preventDefault();

    try {
      setLoading(true);
      setFeedback("");
      const result = await login(loginForm.email, loginForm.contrasenia);
      const nextSession = {
        token: result.access_token,
        rol: result.rol,
        email: loginForm.email,
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(nextSession));
      setSession(nextSession);
      setLoginForm(initialLogin);
    } catch (error) {
      setFeedback(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleRegistro(event, tipo) {
    event.preventDefault();
    const form = tipo === "profesor" ? registroProfesorForm : registroEstudianteForm;
    const action = tipo === "profesor" ? registroProfesor : registroEstudiante;

    try {
      setLoading(true);
      setFeedback("");
      await action(form);
      setFeedback(`Registro de ${tipo} completado. Ya puedes iniciar sesion.`);

      if (tipo === "profesor") {
        setRegistroProfesorForm(initialRegistro);
      } else {
        setRegistroEstudianteForm(initialRegistro);
      }
    } catch (error) {
      setFeedback(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleCrearCurso(event) {
    event.preventDefault();

    try {
      setLoading(true);
      setFeedback("");
      await crearCurso(session.token, cursoForm);
      setCursoForm(initialCurso);
      setFeedback("Curso creado correctamente.");
      await loadDashboard();
    } catch (error) {
      setFeedback(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleInscripcion(cursoId) {
    try {
      setLoading(true);
      setFeedback("");
      await inscribirseEnCurso(session.token, cursoId);
      setFeedback("Inscripcion realizada correctamente.");
      await loadDashboard();
    } catch (error) {
      setFeedback(error.message);
    } finally {
      setLoading(false);
    }
  }

  function handleLogout() {
    localStorage.removeItem(STORAGE_KEY);
    setSession(null);
    setFeedback("");
  }

  return (
    <div className="app-shell">
      <header className="hero">
        <div>
          <p className="eyebrow">Gestion de Cursos</p>
          <h1>Un panel simple para probar toda tu API</h1>
          <p className="hero-copy">
            Puedes entrar, registrar usuarios, crear cursos e inscribirte sin salir del navegador.
          </p>
        </div>

        <div className="session-box">
          {session ? (
            <>
              <span className="badge">{session.rol}</span>
              <strong>{session.email}</strong>
              <button className="ghost-button" onClick={handleLogout}>
                Cerrar sesion
              </button>
            </>
          ) : (
            <>
              <span className="badge muted">sin sesion</span>
              <p>Backend esperado en `http://127.0.0.1:8000`.</p>
            </>
          )}
        </div>
      </header>

      {feedback ? <div className="feedback">{feedback}</div> : null}

      {!session ? (
        <main className="grid-layout auth-layout">
          <section className="panel">
            <h2>Login</h2>
            <form className="stack" onSubmit={handleLogin}>
              <label>
                Email
                <input
                  type="email"
                  value={loginForm.email}
                  onChange={(event) =>
                    setLoginForm({ ...loginForm, email: event.target.value })
                  }
                  required
                />
              </label>
              <label>
                Contrasena
                <input
                  type="password"
                  value={loginForm.contrasenia}
                  onChange={(event) =>
                    setLoginForm({ ...loginForm, contrasenia: event.target.value })
                  }
                  required
                />
              </label>
              <button type="submit" disabled={loading}>
                {loading ? "Entrando..." : "Entrar"}
              </button>
            </form>
          </section>

          <section className="panel">
            <h2>Registro profesor</h2>
            <form className="stack" onSubmit={(event) => handleRegistro(event, "profesor")}>
              <RegistroFields form={registroProfesorForm} setForm={setRegistroProfesorForm} />
              <button type="submit" disabled={loading}>
                Crear profesor
              </button>
            </form>
          </section>

          <section className="panel">
            <h2>Registro estudiante</h2>
            <form className="stack" onSubmit={(event) => handleRegistro(event, "estudiante")}>
              <RegistroFields form={registroEstudianteForm} setForm={setRegistroEstudianteForm} />
              <button type="submit" disabled={loading}>
                Crear estudiante
              </button>
            </form>
          </section>
        </main>
      ) : (
        <main className="grid-layout dashboard-layout">
          <section className="panel">
            <h2>{session.rol === "profesor" ? "Mis cursos" : "Mis inscripciones"}</h2>
            <ItemList
              items={panel.cursos}
              emptyMessage={
                session.rol === "profesor"
                  ? "Todavia no has creado cursos."
                  : "Todavia no tienes inscripciones."
              }
              renderItem={(item) =>
                session.rol === "profesor" ? (
                  <>
                    <strong>{item.titulo}</strong>
                    <p>{item.descripcion || "Sin descripcion"}</p>
                  </>
                ) : (
                  <>
                    <strong>Curso #{item.curso_id}</strong>
                    <p>Inscripcion #{item.id}</p>
                    <p>Calificacion: {item.calificacion ?? "Pendiente"}</p>
                  </>
                )
              }
            />
          </section>

          {session.rol === "profesor" ? (
            <section className="panel">
              <h2>Crear curso</h2>
              <form className="stack" onSubmit={handleCrearCurso}>
                <label>
                  Titulo
                  <input
                    type="text"
                    value={cursoForm.titulo}
                    onChange={(event) =>
                      setCursoForm({ ...cursoForm, titulo: event.target.value })
                    }
                    required
                  />
                </label>
                <label>
                  Descripcion
                  <textarea
                    rows="4"
                    value={cursoForm.descripcion}
                    onChange={(event) =>
                      setCursoForm({ ...cursoForm, descripcion: event.target.value })
                    }
                  />
                </label>
                <button type="submit" disabled={loading}>
                  Guardar curso
                </button>
              </form>
            </section>
          ) : (
            <section className="panel">
              <h2>Todos los cursos</h2>
              <ItemList
                items={panel.todosLosCursos}
                emptyMessage="No hay cursos disponibles."
                renderItem={(item) => (
                  <>
                    <strong>{item.titulo}</strong>
                    <p>{item.descripcion || "Sin descripcion"}</p>
                    <button onClick={() => handleInscripcion(item.id)} disabled={loading}>
                      Inscribirme
                    </button>
                  </>
                )}
              />
            </section>
          )}

          <section className="panel">
            <h2>Profesores</h2>
            <ItemList
              items={panel.profesores}
              emptyMessage="No hay profesores disponibles."
              renderItem={(item) => (
                <>
                  <strong>{item.nombre}</strong>
                  <p>{item.email}</p>
                  <p>{item.especialidad || "Sin especialidad"}</p>
                </>
              )}
            />
          </section>
        </main>
      )}
    </div>
  );
}

function RegistroFields({ form, setForm }) {
  return (
    <>
      <label>
        Nombre
        <input
          type="text"
          value={form.nombre}
          onChange={(event) => setForm({ ...form, nombre: event.target.value })}
          required
        />
      </label>
      <label>
        Email
        <input
          type="email"
          value={form.email}
          onChange={(event) => setForm({ ...form, email: event.target.value })}
          required
        />
      </label>
      <label>
        Contrasena
        <input
          type="password"
          value={form.password}
          onChange={(event) => setForm({ ...form, password: event.target.value })}
          required
        />
      </label>
    </>
  );
}

function ItemList({ items, renderItem, emptyMessage }) {
  if (!items.length) {
    return <p className="empty-state">{emptyMessage}</p>;
  }

  return (
    <div className="list">
      {items.map((item) => (
        <article className="list-item" key={item.id}>
          {renderItem(item)}
        </article>
      ))}
    </div>
  );
}

export default App;
