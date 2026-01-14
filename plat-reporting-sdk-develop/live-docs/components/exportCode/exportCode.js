const sdkExportCodeComponent = Vue.component('sdkExportCodeComponent', {
  template: `
    <div class="expand-code-container">
      <b-button v-b-toggle.expandCode variant="primary">Demo Code</b-button>
      <b-collapse id="expandCode" class="mt-2">
        <b-card :class="{'mt-4': index > 0}" :key="index" v-for="(template, index) of templates">
          <h4 class="card-text">Template {{template.name}}</h4>
          <p class="card-text">
            <b>Element tag:</b>
          </p>
          <pre class="language-javascript" line-numbers>
            <code class="language-javascript">
              {{template.tag}}
            </code>
          </pre>
          <p class="card-text">
            <b>Config:</b>
          </p>
          <pre :id="'content-config-' + index" class="language-javascript" line-numbers>
            <code class="language-javascript">
              {{template.config}}
            </code>
          </pre>
        </b-card>
      </b-collapse>
    </div>
  `,
  props: {
    templates: Array
  }
})
