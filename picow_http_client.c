#include "pico/cyw43_arch.h"
#include "pico/stdlib.h"
#include "hardware/adc.h"
#include "hardware/gpio.h"
#include "pico/stdio.h"
#include "pico/async_context.h"
#include "lwip/altcp_tls.h"
#include "example_http_client_util.h"

#define WIFI_SSID "Nome do Wifi"
#define WIFI_PASS "Senha do Wifi"
#define HOST "10.0.0.123"  // Substitua pelo IP do seu servidor
#define PORT 5000
#define BUTTON_PIN 5  // Pino do botão (ajuste conforme sua placa)
#define SENSOR_ADC 4   // Canal ADC para o sensor extra

void send_data(bool button_state, float temperature) {
    char url[256];
    snprintf(url, sizeof(url), "/data?button=%d&temp=%.2f", 
             button_state, temperature);
    
    EXAMPLE_HTTP_REQUEST_T req = {0};
    req.hostname = HOST;
    req.url = url;
    req.port = PORT;
    req.headers_fn = http_client_header_print_fn;
    req.recv_fn = http_client_receive_print_fn;
    
    printf("Enviando: %s\n", url);
    http_client_request_sync(cyw43_arch_async_context(), &req);
}

float read_onboard_temperature() {
    adc_select_input(4);  // Canal do sensor de temperatura interno
    const float conversion_factor = 3.3f / (1 << 12);
    float adc = (float)adc_read() * conversion_factor;
    return 27.0f - (adc - 0.706f) / 0.001721f;
}

int main() {
    stdio_init_all();
    adc_init();
    gpio_init(BUTTON_PIN);
    gpio_set_dir(BUTTON_PIN, GPIO_IN);
    gpio_pull_up(BUTTON_PIN);  // Ativa resistor de pull-up
    
    if (cyw43_arch_init()) {
        printf("Erro ao inicializar Wi-Fi\n");
        return 1;
    }

    cyw43_arch_enable_sta_mode();
    printf("Conectando ao Wi-Fi...\n");
    
    if (cyw43_arch_wifi_connect_timeout_ms(WIFI_SSID, WIFI_PASS, 
                                          CYW43_AUTH_WPA2_AES_PSK, 10000)) {
        printf("Falha na conexão Wi-Fi\n");
        return 1;
    }
    
    printf("Conectado! IP: %s\n", ip4addr_ntoa(netif_ip4_addr(netif_default)));
    
    while (true) {
        bool button_pressed = !gpio_get(BUTTON_PIN);  // Lógica invertida por causa do pull-up
        float temperature = read_onboard_temperature();
        
        printf("Botão: %d, Temp: %.2f°C\n", button_pressed, temperature);
        send_data(button_pressed, temperature);
        
        sleep_ms(1000);  // Envia a cada 1 segundo
    }

    cyw43_arch_deinit();
    return 0;
}