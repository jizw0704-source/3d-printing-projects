"use strict";
(() => {
  const canvas = document.querySelector("canvas");
  const status = document.querySelector("#status");
  const retry = document.querySelector("#retry");
  const yaw = document.querySelector("#yaw");
  const pitch = document.querySelector("#pitch");
  const zoom = document.querySelector("#zoom");
  const buttons = [...document.querySelectorAll("[data-view]")];
  const controls = [...document.querySelectorAll(".toolbar button, input")];
  const gl = canvas.getContext("webgl", { antialias: true });
  let program,
    buffer,
    count = 0,
    ready = false,
    drag = null;
  const loc = {};
  function shader(type, source) {
    const s = gl.createShader(type);
    gl.shaderSource(s, source);
    gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS))
      throw new Error("渲染器初始化失败");
    return s;
  }
  function initialize() {
    program = gl.createProgram();
    gl.attachShader(
      program,
      shader(
        gl.VERTEX_SHADER,
        `
      attribute vec3 p; attribute vec3 n;
      uniform float yaw, pitch, zoom, aspect;
      varying vec3 normal;
      vec3 turn(vec3 v) {
        vec3 a = vec3(cos(yaw)*v.x+sin(yaw)*v.z,v.y,-sin(yaw)*v.x+cos(yaw)*v.z);
        return vec3(a.x,cos(pitch)*a.y-sin(pitch)*a.z,sin(pitch)*a.y+cos(pitch)*a.z);
      }
      void main(){vec3 q=turn(p);normal=turn(n);gl_Position=vec4(q.x*zoom/(105.*aspect),q.y*zoom/105.,-q.z/300.,1.);}
    `,
      ),
    );
    gl.attachShader(
      program,
      shader(
        gl.FRAGMENT_SHADER,
        `
      precision mediump float; varying vec3 normal;
      void main(){vec3 n=normalize(normal);float light=.38+.5*max(dot(n,normalize(vec3(-.45,.6,1.))),0.)+.12*max(dot(n,normalize(vec3(.8,-.3,.5))),0.);gl_FragColor=vec4(vec3(.47,.60,.55)*light,1.);}
    `,
      ),
    );
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS))
      throw new Error("渲染器初始化失败");
    gl.useProgram(program);
    for (const name of ["yaw", "pitch", "zoom", "aspect"])
      loc[name] = gl.getUniformLocation(program, name);
    buffer = gl.createBuffer();
  }
  function draw() {
    if (!ready) return;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(canvas.clientWidth * dpr);
    canvas.height = Math.round(canvas.clientHeight * dpr);
    gl.viewport(0, 0, canvas.width, canvas.height);
    gl.enable(gl.DEPTH_TEST);
    gl.clearColor(0.969, 0.969, 0.969, 1);
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    gl.uniform1f(loc.yaw, (Number(yaw.value) * Math.PI) / 180);
    gl.uniform1f(loc.pitch, (Number(pitch.value) * Math.PI) / 180);
    gl.uniform1f(loc.zoom, Number(zoom.value));
    gl.uniform1f(loc.aspect, canvas.width / canvas.height);
    gl.drawArrays(gl.TRIANGLES, 0, count);
  }
  function clearSelection() {
    buttons.forEach((b) => b.setAttribute("aria-pressed", "false"));
  }
  function view(name) {
    const views = {
      iso: [-28, 18, 1],
      front: [0, 0, 1],
      side: [90, 0, 1],
      end: [
        0,
        -90,
        Math.min(3, (canvas.clientWidth / canvas.clientHeight) * 4),
      ],
    };
    [yaw.value, pitch.value, zoom.value] = views[name];
    clearSelection();
    buttons
      .find((b) => b.dataset.view === name)
      .setAttribute("aria-pressed", "true");
    draw();
  }
  async function load() {
    ready = false;
    controls.forEach((c) => (c.disabled = true));
    retry.hidden = true;
    status.textContent = "正在加载模型…";
    try {
      if (!gl) throw new Error("当前浏览器不支持三维预览，请下载模型查看");
      if (!program) initialize();
      const response = await fetch("mesh.bin");
      if (!response.ok) throw new Error("模型文件加载失败");
      const data = new Float32Array(await response.arrayBuffer());
      if (!data.length || data.length % 18)
        throw new Error("模型数据为空或不完整");
      count = data.length / 6;
      gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
      gl.bufferData(gl.ARRAY_BUFFER, data, gl.STATIC_DRAW);
      for (const [name, offset] of [
        ["p", 0],
        ["n", 12],
      ]) {
        const a = gl.getAttribLocation(program, name);
        gl.enableVertexAttribArray(a);
        gl.vertexAttribPointer(a, 3, gl.FLOAT, false, 24, offset);
      }
      ready = true;
      controls.forEach((c) => (c.disabled = false));
      status.textContent = "模型已加载 · V04";
      view("iso");
    } catch (error) {
      status.textContent = error.message;
      retry.hidden = false;
    }
  }
  buttons.forEach((b) =>
    b.addEventListener("click", () => view(b.dataset.view)),
  );
  document.querySelector("#reset").addEventListener("click", () => view("iso"));
  [yaw, pitch, zoom].forEach((c) =>
    c.addEventListener("input", () => {
      clearSelection();
      draw();
    }),
  );
  function rotate(dx, dy) {
    yaw.value = ((Number(yaw.value) + dx + 540) % 360) - 180;
    pitch.value = Math.max(-90, Math.min(90, Number(pitch.value) + dy));
    clearSelection();
    draw();
  }
  function scale(delta) {
    zoom.value = Math.max(0.5, Math.min(4, Number(zoom.value) + delta));
    draw();
  }
  canvas.addEventListener("pointerdown", (e) => {
    if (!ready) return;
    drag = [e.clientX, e.clientY];
    canvas.setPointerCapture(e.pointerId);
    canvas.focus({ preventScroll: true });
  });
  canvas.addEventListener("pointermove", (e) => {
    if (!drag) return;
    rotate((e.clientX - drag[0]) * 0.6, (e.clientY - drag[1]) * 0.5);
    drag = [e.clientX, e.clientY];
  });
  for (const name of ["pointerup", "pointercancel", "lostpointercapture"])
    canvas.addEventListener(name, () => (drag = null));
  canvas.addEventListener(
    "wheel",
    (e) => {
      if (!ready) return;
      e.preventDefault();
      scale(-e.deltaY * 0.001);
    },
    { passive: false },
  );
  canvas.addEventListener("keydown", (e) => {
    if (!ready) return;
    const actions = {
      ArrowLeft: () => rotate(-5, 0),
      ArrowRight: () => rotate(5, 0),
      ArrowUp: () => rotate(0, -5),
      ArrowDown: () => rotate(0, 5),
      "+": () => scale(0.1),
      "=": () => scale(0.1),
      "-": () => scale(-0.1),
      Home: () => view("iso"),
    };
    if (actions[e.key]) {
      e.preventDefault();
      actions[e.key]();
    }
  });
  retry.addEventListener("click", load);
  new ResizeObserver(draw).observe(canvas);
  canvas.addEventListener("webglcontextlost", (e) => {
    e.preventDefault();
    ready = false;
    controls.forEach((c) => (c.disabled = true));
    status.textContent = "三维显示已中断，请刷新页面";
  });
  load();
})();
