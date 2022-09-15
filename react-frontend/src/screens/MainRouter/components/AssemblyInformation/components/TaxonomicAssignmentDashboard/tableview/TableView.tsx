import React, { createContext } from 'react';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col'
import Container from 'react-bootstrap/esm/Container';

// Stylesheet
import 'bootstrap/dist/css/bootstrap.min.css';
import SelectionModeSelector from './Components/SelectionModeSelector';
import SelectionTable from './Components/SelectionTable';
import ColumnSelector from './Components/ColumnSelector'
import { fetchTaxaminerMain } from '../../../../../../../api';



interface Props {
    data: []
    keys: Set<string>
    setSelectMode: any
    passClick: any
    dataset_id: number
    userID: number
    token: string
}
  
interface State {
    aa_seq: string
    camera: any
    select_mode: string
    selected_data: Set<string>
    data: any
    col_keys: string[]
}
  

class TableView extends React.Component<Props, State> {
    // Set up states for loading data
	constructor(props: any){
		super(props);
		this.state ={ 
            // selected_row: {g_name: "Pick a gene", taxonomic_assignment: "Pick a gene", plot_label: "Pick a gene", best_hit: "Pick a gene", c_name: "Pick a gene", bh_evalue: 0, best_hitID: "None"}, 
            aa_seq: "Pick a gene",
            camera: null,
            select_mode: 'neutral',
            selected_data: new Set(),
            data: undefined,
            col_keys: ["plot_label", "g_name", "bh_evalue"]
        }
	}

    /**
	 * Call API on component mount to load plot data
	 */
	componentDidMount() {
		fetchTaxaminerMain(1, 1, this.props.userID, this.props.token)
        .then((data) => {
            this.setState( {data: data})
        })
	}

    /**
     * Update table columns
     * @param cols array of col names (keys)
     */
    setTableCols = (cols: string[]) => {
        this.setState({col_keys: cols})
    }

    render() {
        return (
            <Container fluid>
                <Row>
                    <Col xs={7}>
                        <SelectionTable
                        master_data={this.props.data}
                        keys={this.props.keys}
                        // pass table click events up
                        passClick={this.props.passClick}
                        col_keys = {this.state.col_keys}
                        />
                    </Col>
                    <Col>
                        <Row>
                            
                        </Row>
                        <Row>
                            <SelectionModeSelector
                            passMode = {this.props.setSelectMode}
                            selection = {this.props.keys}
                            dataset_id = {this.props.dataset_id}
                            />
                        </Row>
                        <Row>
                            <ColumnSelector
                            passColsUp = {this.setTableCols}
                            />
                        </Row>
                    </Col>
                </Row>
        </Container>
        );
    } 
}

export { TableView }