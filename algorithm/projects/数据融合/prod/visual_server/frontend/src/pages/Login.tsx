import { Button, Card, Form, Input, message } from "antd";
import { Navigate } from "react-router-dom";
import { useAuth } from "../auth";

export default function LoginPage() {
  const { token, login } = useAuth();
  if (token) return <Navigate to="/execute" replace />;
  return (
    <div style={{ maxWidth: 420, margin: "10vh auto" }}>
      <Card title="登录 · 多光谱拼图管控台">
        <Form
          layout="vertical"
          onFinish={async (v) => {
            try {
              await login(v.username, v.password);
            } catch (e: any) {
              message.error(e.message || "登录失败");
            }
          }}
        >
          <Form.Item name="username" label="用户名" rules={[{ required: true }]}>
            <Input autoFocus />
          </Form.Item>
          <Form.Item name="password" label="密码" rules={[{ required: true }]}>
            <Input.Password />
          </Form.Item>
          <Button type="primary" htmlType="submit" block>
            登录
          </Button>
        </Form>
      </Card>
    </div>
  );
}
