`timescale 1ns/1ps

module cpu_tb;
    reg clk = 1'b0;
    reg rst = 1'b1;

    wire [31:0] pc_value;
    wire        parity_error;
    integer     cycle_count = 0;

    cpu_top dut (
        .clk         (clk),
        .rst         (rst),
        .pc_value    (pc_value),
        .parity_error(parity_error)
    );

    // Clock generation
    always #5 clk = ~clk;

    initial begin
        $display("Starting tinyml_risc_cpu simulation");
        #20 rst = 1'b0;
    end

    task automatic display_registers;
        integer i;
        begin
            $display("Register file snapshot:");
            for (i = 0; i < 16; i = i + 1) begin
                if (i % 4 == 0) begin
                    $write("   ");
                end
                $write("R%0d=%h ", i, dut.regfile_i.regs[i]);
                if (i % 4 == 3) begin
                    $display("");
                end
            end
            $display("");
        end
    endtask

    always @(posedge clk) begin
        if (rst) begin
            cycle_count <= 0;
            $display("[RESET] PC=%0d", pc_value);
        end else begin
            cycle_count <= cycle_count + 1;
            $display("---- Cycle %0d ----", cycle_count);
            $display("PC=%0d (0x%08h) INSTR=0x%08h OPCODE=0x%1h", pc_value, pc_value, dut.instruction, dut.opcode);
            $display("ALU=%0d (0x%08h) PARITY_ERR=%b", $signed(dut.alu_result), dut.alu_result, parity_error);
            display_registers();

            if (dut.opcode == 4'b1000) begin
                $display("   -> MAC4 executing: result=%0d (0x%08h)", $signed(dut.alu_result), dut.alu_result);
            end

            if (pc_value >= 32'd32) begin
                $display("Program complete. Final MAC4 result stored in R3=%0d (0x%08h)", $signed(dut.regfile_i.regs[3]), dut.regfile_i.regs[3]);
                $finish;
            end
        end
    end

    initial begin
        #500;
        $display("Timeout - terminating simulation");
        $finish;
    end
endmodule
