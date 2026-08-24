import { createRouter, createWebHistory } from "vue-router";
import HomeView from "./views/HomeView.vue";
import AlgoView from "./views/AlgoView.vue";

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "home", component: HomeView },
    { path: "/algo/:id", name: "algo", component: AlgoView, props: true },
  ],
  scrollBehavior() {
    return { top: 0 };
  },
});
