const LitElement = Object.getPrototypeOf(
  customElements.get("ha-panel-lovelace")
);
const html = LitElement.prototype.html;
const css = LitElement.prototype.css;

class SystemairAlarmHistoryCardEditor extends LitElement {
  static get properties() {
    return {
      hass: {},
      _config: {},
    };
  }

  setConfig(config) {
    this._config = config;
  }

  _valueChanged(ev) {
    if (!this.hass) {
      return;
    }
    const newConfig = ev.detail.value;
    
    const event = new CustomEvent("config-changed", {
      detail: { config: newConfig },
      bubbles: true,
      composed: true,
    });
    this.dispatchEvent(event);
  }

  render() {
    if (!this.hass || !this._config) {
      return html``;
    }

    const schema = [
      { 
        name: "entity", 
        required: true,
        selector: { 
          entity: { 
            filter: [{ integration: "systemair", domain: "sensor", attribute: "history" }]
          } 
        } 
      },
      { 
        name: "title", 
        required: false, 
        selector: { 
          text: {}
        } 
      },
    ];

    return html`
      <ha-form
        .hass=${this.hass}
        .data=${this._config}
        .schema=${schema}
        @value-changed=${this._valueChanged}
      ></ha-form>
    `;
  }
}
customElements.define("systemair-alarm-history-card-editor", SystemairAlarmHistoryCardEditor);

class SystemairAlarmHistoryCard extends LitElement {
  static get properties() {
    return {
      hass: {},
      config: {},
    };
  }

  get _isInGallery() {
    return this.parentElement?.classList.contains('preview');
  }

  static async getConfigElement() {
    return document.createElement("systemair-alarm-history-card-editor");
  }

  static getStubConfig(hass) {
    const historySensor = Object.values(hass.states).find(
      (state) => 
        state.attributes.history && 
        Array.isArray(state.attributes.history) &&
        hass.entities[state.entity_id]?.platform === "systemair"
    );
    
    return {
      type: "custom:systemair-alarm-history-card",
      entity: historySensor ? historySensor.entity_id : "",
      title: "Alarm History",
    };
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error("You need to define an entity");
    }
    this.config = config;
  }

  getCardSize() {
    if (this._isInGallery) {
        return 3;
    }
    const history = this.hass?.states[this.config.entity]?.attributes?.history || [];
    return history.length > 0 ? Math.min(history.length, 10) + 1 : 2;
  }

  render() {
    if (!this.hass || !this.config) {
      return html``;
    }

    const stateObj = this.hass.states[this.config.entity];
    if (!stateObj) {
      return html`
        <ha-card>
          <div class="card-content">
            <div class="warning">
              Entity not found: ${this.config.entity}
            </div>
          </div>
        </ha-card>
      `;
    }

    const history = stateObj.attributes.history || [];
    const displayHistory = this._isInGallery ? history.slice(0, 2) : history;

    return html`
      <ha-card .header="${this.config.title || 'Alarm History'}">
        <div class="card-content">
          ${displayHistory.length > 0
            ? html`
                <table>
                  <thead>
                    <tr>
                      <th class="timestamp">Timestamp</th>
                      <th class="event">Event</th>
                      <th class="status">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    ${displayHistory.map(
                      (item) => html`
                        <tr>
                          <td>${item.timestamp}</td>
                          <td>${item.alarm}</td>
                          <td>${item.status}</td>
                        </tr>
                      `
                    )}
                  </tbody>
                </table>
              `
            : html`
                <div class="no-history">
                  No alarm history records found.
                </div>
              `}
        </div>
      </ha-card>
    `;
  }

  static get styles() {
    return css`
      .warning {
        color: var(--error-color);
        padding: 16px;
      }
      .no-history {
        padding: 16px;
        text-align: center;
      }
      table {
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed;
      }
      th, td {
        padding: 8px;
        text-align: left;
        border-bottom: 1px solid var(--divider-color);
        word-break: break-word;
      }
      th {
        font-weight: bold;
      }
      tbody tr:last-child td {
        border-bottom: none;
      }
      .timestamp { width: 38%; }
      .event { width: 42%; }
      .status { width: 20%; }
    `;
  }
}

customElements.define("systemair-alarm-history-card", SystemairAlarmHistoryCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "systemair-alarm-history-card",
  name: "Systemair Alarm History Card",
  description: "Displays the alarm history from the Systemair integration.",
  preview: true,
  documentationURL: "https://github.com/AN3Orik/systemair",
});