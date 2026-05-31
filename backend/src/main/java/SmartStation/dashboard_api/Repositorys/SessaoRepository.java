package SmartStation.dashboard_api.Repositorys;

import SmartStation.dashboard_api.Models.SessaoModel;
import org.springframework.data.jpa.repository.JpaRepository;

public interface SessaoRepository extends JpaRepository<SessaoModel, Long> {
}
