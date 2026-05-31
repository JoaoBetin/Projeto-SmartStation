package SmartStation.dashboard_api.Repositorys;

import SmartStation.dashboard_api.Models.CaixaModel;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CaixaRepository extends JpaRepository<CaixaModel, Long> {
}