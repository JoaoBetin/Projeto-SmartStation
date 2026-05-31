package SmartStation.dashboard_api.DTOs;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.time.LocalTime;

@NoArgsConstructor
@AllArgsConstructor
@Data
public class SessaoDTO {

    private Long id;

    private Boolean ativa;

    private LocalDate data;

    private LocalTime horaInicio;

    private LocalTime horaFim;

    private LocalTime tempoOcioso;

    private Integer totalCaixas;

    private Long funcionarioID;
}
