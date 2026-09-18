import { Layout, Menu, Typography } from "antd";
import { Link, Navigate, Route, Routes, useLocation } from "react-router-dom";
import { BrowserRouter } from "react-router-dom";
import { useAuth } from "./auth";
import LoginPage from "./pages/Login";
import ProfilesPage from "./pages/Profiles";
import ExecutePage from "./pages/Execute";
import JobsPage from "./pages/Jobs";
import CliGuidePage from "./pages/CliGuide";

const { Header, Content } = Layout;

function Shell() {
  const { token, logout } = useAuth();
  const loc = useLocation();
  if (!token) return <Navigate to="/login" replace />;
  const key = loc.pathname.split("/")[1] || "execute";
  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Header style={{ display: "flex", alignItems: "center", gap: 24 }}>
        <Typography.Title level={4} style={{ color: "#fff", margin: 0 }}>
          多光谱拼图管控台
        </Typography.Title>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[key]}
          items={[
            { key: "execute", label: <Link to="/execute">执行台</Link> },
            { key: "profiles", label: <Link to="/profiles">参数配置</Link> },
            { key: "jobs", label: <Link to="/jobs">执行记录</Link> },
            { key: "cli", label: <Link to="/cli">命令行教学</Link> },
          ]}
          style={{ flex: 1, minWidth: 0 }}
        />
        <a style={{ color: "#fff" }} onClick={logout}>
          退出
        </a>
      </Header>
      <Content style={{ padding: 24 }}>
        <Routes>
          <Route path="/execute" element={<ExecutePage />} />
          <Route path="/profiles" element={<ProfilesPage />} />
          <Route path="/jobs" element={<JobsPage />} />
          <Route path="/cli" element={<CliGuidePage />} />
          <Route path="*" element={<Navigate to="/execute" replace />} />
        </Routes>
      </Content>
    </Layout>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/*" element={<Shell />} />
      </Routes>
    </BrowserRouter>
  );
}
