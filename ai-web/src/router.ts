import { createRouter, createWebHistory } from "vue-router";
import HomeView from "./views/HomeView.vue";
import LayerView from "./views/LayerView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "home", component: HomeView },
    { path: "/layer/:id", name: "layer", component: LayerView, props: true },
    { path: "/algo/:id", redirect: "/" },
  ],
});

export default router;
