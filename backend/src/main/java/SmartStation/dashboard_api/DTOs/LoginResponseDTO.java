package SmartStation.dashboard_api.DTOs;

import SmartStation.dashboard_api.Enums.Cargo;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class LoginResponseDTO {

    private Long id;

    private String nome;

    private Long matricula;

    private Cargo cargo;
}