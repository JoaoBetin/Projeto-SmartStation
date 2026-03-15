package SmartStation.dashboard_api.Caixa;

import SmartStation.dashboard_api.Sessao.SessaoModel;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class CaixaDTO {

    private Long id;

    private Long sessaoId;

    private LocalDateTime inicio_deteccao;

    private LocalDateTime fim_deteccao;

    private Long tempo_detectado;
}