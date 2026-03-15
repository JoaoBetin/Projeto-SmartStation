package SmartStation.dashboard_api.Caixa;

import SmartStation.dashboard_api.Sessao.SessaoModel;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Entity
@Table(name = "caixa_detectada")
@NoArgsConstructor
@AllArgsConstructor
public class CaixaModel {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    @JoinColumn(name = "sessao_id")
    private SessaoModel sessaoModel;

    private LocalDateTime inicio_deteccao;

    private LocalDateTime fim_deteccao;

    private Long tempo_detectado;
}