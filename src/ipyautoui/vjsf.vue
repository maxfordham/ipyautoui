<template>
  <div>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@koumoul/vjsf@latest/dist/main.css">
    <div v-if="vjsf_loaded">
      <v-form v-model="valid">
        <v-jsf v-model="value" :schema="schema"></v-jsf>
      </v-form>
    </div>
  </div>    
</template>
<!-- // <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/easymde/dist/easymde.min.css">
// <script src="https://cdn.jsdelivr.net/npm/easymde/dist/easymde.min.js"></script> -->
<script>
    
import EasyMDE from 'easymde/dist/easymde.min.js'
import 'easymde/dist/easymde.min.css'
global.EasyMDE = EasyMDE
// ^ this isn't working

module.exports = {
    async created() {
        const [VJsf] = await this.import(['https://cdn.jsdelivr.net/npm/@koumoul/vjsf@latest/dist/main.js']);
        this.$options.components['v-jsf'] = VJsf.default;
        this.vjsf_loaded = true;
    },
    methods: {
        import(deps) {
          return this.loadRequire()
              .then(() => new Promise((resolve, reject) => {
                requirejs(deps, (...modules) => resolve(modules));
              }));
        },
        loadRequire() {
          /* Needed in lab */
          if (window.requirejs) {
              console.log('require found');
              return Promise.resolve()
          }
          return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.6/require.min.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
          });
        }
    }
}
</script>